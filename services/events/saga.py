import uuid, asyncio
from enum import Enum
from typing import List, Dict, Any, Callable, Optional
from datetime import datetime, timezone
from packages.common.logger import get_logger
from packages.events.schemas import SagaStepEvent
from packages.events.bus import get_event_bus

logger = get_logger("saga-orchestrator")

class SagaStatus(str, Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    COMPENSATING = "COMPENSATING"
    FAILED = "FAILED"

class SagaStep:
    def __init__(self, name: str, action: Callable[..., Any], compensate: Optional[Callable[..., Any]] = None):
        self.name = name
        self.action = action
        self.compensate = compensate

class SagaInstance:
    def __init__(self, saga_name: str, steps: List[SagaStep]):
        self.saga_id = str(uuid.uuid4())
        self.saga_name = saga_name
        self.steps = steps
        self.status = SagaStatus.PENDING
        self.executed_steps: List[SagaStep] = []
        self.context: Dict[str, Any] = {}
        self.error: Optional[str] = None

    async def execute(self, initial_context: Dict[str, Any]) -> bool:
        self.context = dict(initial_context)
        self.status = SagaStatus.IN_PROGRESS
        bus = get_event_bus()

        for step in self.steps:
            try:
                logger.info(f"Saga [{self.saga_name}:{self.saga_id}] executing step: {step.name}")
                await bus.publish("sagas.events", SagaStepEvent(
                    partition_key=self.saga_id,
                    saga_id=self.saga_id,
                    saga_name=self.saga_name,
                    step=step.name,
                    status="STARTED"
                ))

                if asyncio.iscoroutinefunction(step.action):
                    res = await step.action(self.context)
                else:
                    res = step.action(self.context)

                if isinstance(res, dict):
                    self.context.update(res)

                self.executed_steps.append(step)
                await bus.publish("sagas.events", SagaStepEvent(
                    partition_key=self.saga_id,
                    saga_id=self.saga_id,
                    saga_name=self.saga_name,
                    step=step.name,
                    status="COMPLETED"
                ))
            except Exception as e:
                logger.error(f"Saga [{self.saga_name}:{self.saga_id}] step {step.name} failed: {e}")
                self.error = str(e)
                self.status = SagaStatus.COMPENSATING
                await self._compensate()
                return False

        self.status = SagaStatus.COMPLETED
        return True

    async def _compensate(self):
        bus = get_event_bus()
        logger.warning(f"Saga [{self.saga_name}:{self.saga_id}] triggering compensations for {len(self.executed_steps)} steps")

        for step in reversed(self.executed_steps):
            if step.compensate:
                try:
                    logger.info(f"Saga [{self.saga_name}:{self.saga_id}] compensating step: {step.name}")
                    if asyncio.iscoroutinefunction(step.compensate):
                        await step.compensate(self.context)
                    else:
                        step.compensate(self.context)
                    await bus.publish("sagas.events", SagaStepEvent(
                        partition_key=self.saga_id,
                        saga_id=self.saga_id,
                        saga_name=self.saga_name,
                        step=step.name,
                        status="COMPENSATED"
                    ))
                except Exception as comp_err:
                    logger.error(f"Compensation error in step {step.name}: {comp_err}")

        self.status = SagaStatus.FAILED
