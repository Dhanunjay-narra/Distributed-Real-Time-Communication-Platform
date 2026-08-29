import pytest
import pytest_asyncio
from packages.common.database import DatabaseManager, Base
from packages.contracts.auth import RegisterRequest
from packages.contracts.messages import SendMessageRequest, MessageType
from packages.contracts.sync import SyncPullRequest
from services.auth.service import AuthService
from services.conversations.service import ConversationService
from services.messaging.service import MessagingService
from services.sync.service import SyncService
from services.sync.vector_clock import VectorClock

def test_vector_clock_causality_and_concurrency():
    vc_a = VectorClock({"A": 1, "B": 0})
    vc_a.increment("A")

    vc_b = VectorClock({"A": 1, "B": 1})

    vc_old = VectorClock({"A": 1, "B": 0})
    assert vc_a.is_causally_newer(vc_old) is True
    assert vc_old.is_causally_newer(vc_a) is False
    assert vc_a.is_concurrent_with(vc_b) is True

    vc_merged = vc_a.merge(vc_b)
    assert vc_merged.get("A") == 2
    assert vc_merged.get("B") == 1
    assert vc_merged.is_causally_newer(vc_a) is True
    assert vc_merged.is_causally_newer(vc_b) is True

@pytest_asyncio.fixture
async def test_db():
    db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with db_manager.session_factory() as session:
        yield session
    await db_manager.close()

@pytest.mark.asyncio
async def test_multi_device_delta_sync_and_offline_recovery(test_db):
    auth_svc = AuthService(test_db)
    conv_svc = ConversationService(test_db)
    msg_svc = MessagingService(test_db)
    sync_svc = SyncService(test_db)

    alice, _ = await auth_svc.register(RegisterRequest(username="alice_sync", display_name="Alice", email="alice_sync@test.com", password="Password123!"))
    bob, _ = await auth_svc.register(RegisterRequest(username="bob_sync", display_name="Bob", email="bob_sync@test.com", password="Password123!"))

    conv = await conv_svc.create_or_get_direct(alice.id, bob.id)

    m1 = await msg_svc.send_message(bob.id, SendMessageRequest(
        idempotency_key="sync-msg-1",
        conversation_id=conv.id,
        content="Hey Alice, message 1"
    ))
    m2 = await msg_svc.send_message(bob.id, SendMessageRequest(
        idempotency_key="sync-msg-2",
        conversation_id=conv.id,
        content="Message 2 sent while laptop was off"
    ))

    pull_req = SyncPullRequest(device_id="alice-laptop", since_sequence=0, limit=50)
    deltas = await sync_svc.pull_deltas(alice.id, pull_req)
    assert len(deltas.messages) == 2
    assert deltas.latest_sequence == 2
    assert deltas.messages[0].content == "Hey Alice, message 1"
    assert deltas.messages[1].content == "Message 2 sent while laptop was off"

    offline_msg = SendMessageRequest(
        idempotency_key="alice-flight-msg-1",
        conversation_id=conv.id,
        content="Replying from the plane offline queue"
    )
    reconciled = await sync_svc.reconcile_offline_outbox(alice.id, "alice-phone", [offline_msg])
    assert len(reconciled) == 1
    assert reconciled[0].sequence_number == 3

    new_pull = SyncPullRequest(device_id="alice-laptop", since_sequence=2, limit=50)
    new_deltas = await sync_svc.pull_deltas(alice.id, new_pull)
    assert len(new_deltas.messages) == 1
    assert new_deltas.messages[0].content == "Replying from the plane offline queue"
