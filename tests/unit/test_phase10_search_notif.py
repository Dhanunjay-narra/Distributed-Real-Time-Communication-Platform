import pytest
import pytest_asyncio
from packages.common.database import DatabaseManager, Base
from packages.contracts.auth import RegisterRequest
from packages.contracts.messages import SendMessageRequest
from packages.events.schemas import NotificationRequestedEvent
from services.auth.service import AuthService
from services.conversations.service import ConversationService
from services.messaging.service import MessagingService
from services.notifications.service import NotificationService
from services.search.service import SearchService

@pytest.mark.asyncio
async def test_notification_pipeline():
    notif_svc = NotificationService()
    user_id = "usr-notif-001"

    # 1. Send active notification
    evt = NotificationRequestedEvent(
        partition_key=user_id,
        recipient_id=user_id,
        title="Alex sent a message",
        body="Hey, are we still meeting today?"
    )
    sent = await notif_svc.send_push_notification(evt)
    assert sent is True
    records = notif_svc.get_sent_notifications(user_id)
    assert len(records) == 1
    assert records[0]["body"] == "Hey, are we still meeting today?"

    # 2. Preference suppression (Muted / DND)
    notif_svc.set_preferences(user_id, enabled=False)
    sent_muted = await notif_svc.send_push_notification(evt)
    assert sent_muted is False

@pytest_asyncio.fixture
async def test_db():
    db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with db_manager.session_factory() as session:
        yield session
    await db_manager.close()

@pytest.mark.asyncio
async def test_full_text_message_search(test_db):
    auth_svc = AuthService(test_db)
    conv_svc = ConversationService(test_db)
    msg_svc = MessagingService(test_db)
    search_svc = SearchService(test_db)

    u1, _ = await auth_svc.register(RegisterRequest(username="u1_search", display_name="User 1", email="u1_search@test.com", password="Password123!"))
    u2, _ = await auth_svc.register(RegisterRequest(username="u2_search", display_name="User 2", email="u2_search@test.com", password="Password123!"))

    conv = await conv_svc.create_or_get_direct(u1.id, u2.id)

    await msg_svc.send_message(u1.id, SendMessageRequest(idempotency_key="s1", conversation_id=conv.id, content="Kafka cluster deployed on Kubernetes"))
    await msg_svc.send_message(u2.id, SendMessageRequest(idempotency_key="s2", conversation_id=conv.id, content="Postgres replication is healthy"))
    await msg_svc.send_message(u1.id, SendMessageRequest(idempotency_key="s3", conversation_id=conv.id, content="Reviewing PR for WebSockets"))

    # Search for 'Kafka'
    results = await search_svc.search_messages(user_id=u1.id, query="Kafka")
    assert len(results) == 1
    assert "Kubernetes" in results[0].content

    # Search for 'replication'
    results_rep = await search_svc.search_messages(user_id=u1.id, query="replication")
    assert len(results_rep) == 1
    assert "healthy" in results_rep[0].content
