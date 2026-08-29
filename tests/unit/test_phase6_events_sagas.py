import pytest, asyncio
from packages.events.schemas import MessageSentEvent
from services.events.consumers import ConsumerGroup, dlq
from services.events.saga import SagaInstance, SagaStep, SagaStatus

@pytest.mark.asyncio
async def test_consumer_group_and_dlq_routing():
    consumer = ConsumerGroup("notification-worker", max_retries=2)
    processed = []

    # 1. Successful handler
    async def happy_handler(evt):
        processed.append(evt.message_id)

    consumer.register("message.sent", happy_handler)
    evt = MessageSentEvent(
        partition_key="conv-1",
        message_id="msg-ok-1",
        conversation_id="conv-1",
        sender_id="u1",
        sequence_number=1,
        content="Success"
    )
    await consumer.process_event("messages.sent", evt)
    assert len(processed) == 1
    assert processed[0] == "msg-ok-1"

    # 2. Failing handler that exhausts retries and routes to DLQ
    failing_consumer = ConsumerGroup("failing-worker", max_retries=2)
    async def faulty_handler(evt):
        raise RuntimeError("Downstream third-party push gateway timeout")

    failing_consumer.register("message.sent", faulty_handler)
    bad_evt = MessageSentEvent(
        partition_key="conv-1",
        message_id="msg-err-999",
        conversation_id="conv-1",
        sender_id="u1",
        sequence_number=2,
        content="Failed push"
    )
    await failing_consumer.process_event("messages.sent", bad_evt)
    
    dlq_records = dlq.list_records()
    assert len(dlq_records) >= 1
    assert any(r["event_id"] == bad_evt.event_id for r in dlq_records)

@pytest.mark.asyncio
async def test_saga_orchestrator_success_and_compensation():
    audit_log = []

    # Step 1: Create Group Record
    async def create_group_action(ctx):
        audit_log.append("STEP1_CREATED_GROUP")
        return {"group_id": "grp-100"}

    async def create_group_compensate(ctx):
        audit_log.append("COMPENSATE_STEP1_DELETE_GROUP")

    # Step 2: Add Members
    async def add_members_action(ctx):
        audit_log.append("STEP2_ADD_MEMBERS")
        return {"members_added": True}

    async def add_members_compensate(ctx):
        audit_log.append("COMPENSATE_STEP2_REMOVE_MEMBERS")

    # Happy Saga Execution
    saga_ok = SagaInstance("CreateGroupSaga", [
        SagaStep("CreateGroup", create_group_action, create_group_compensate),
        SagaStep("AddMembers", add_members_action, add_members_compensate),
    ])
    success = await saga_ok.execute({"creator": "u1", "name": "Dev Team"})
    assert success is True
    assert saga_ok.status == SagaStatus.COMPLETED
    assert "STEP1_CREATED_GROUP" in audit_log
    assert "STEP2_ADD_MEMBERS" in audit_log

    # Failing Saga Execution with Automatic Rollback
    audit_log.clear()

    async def faulty_step_action(ctx):
        raise ValueError("Failed to allocate conversation container partition")

    saga_fail = SagaInstance("FailingGroupSaga", [
        SagaStep("CreateGroup", create_group_action, create_group_compensate),
        SagaStep("AddMembers", add_members_action, add_members_compensate),
        SagaStep("FaultyStep", faulty_step_action, None),
    ])
    fail_res = await saga_fail.execute({"creator": "u1", "name": "Faulty Group"})
    assert fail_res is False
    assert saga_fail.status == SagaStatus.FAILED
    assert "COMPENSATE_STEP2_REMOVE_MEMBERS" in audit_log
    assert "COMPENSATE_STEP1_DELETE_GROUP" in audit_log
