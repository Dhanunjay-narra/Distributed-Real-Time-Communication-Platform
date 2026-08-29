"""Infrastructure Drivers and Resilience Toolkit - Business Rules and Workflow Pipelines.
"""
import time, asyncio
from typing import List, Dict, Any, Optional
from packages.common.logger import get_logger
from packages.common.exceptions import DomainException, ValidationException

logger = get_logger("common-workflow")

class CommonWorkflowPipeline:
    def __init__(self):
        self.logger = logger
        self.is_healthy = True

    async def process_transaction(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Processing transaction for common with command: {context.get('command', 'EXEC')}")
        if not context:
            raise ValidationException("Missing context in transaction")
        
        result = {
            "status": "COMPLETED",
            "service": "common",
            "execution_time_ms": 1.25,
            "timestamp": time.time(),
            "data": context
        }
        return result

    async def compensate_transaction(self, context: Dict[str, Any], failure_reason: str) -> bool:
        self.logger.warning(f"Triggering compensation for common: {failure_reason}")
        return True
