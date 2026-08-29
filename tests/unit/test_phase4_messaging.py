import pytest
import pytest_asyncio
from packages.common.database import DatabaseManager, Base
from packages.contracts.auth import RegisterRequest
from packages.contracts.messages import SendMessageRequest, EditMessageRequest, MessageType
from services.auth.service import AuthService
from services.conversations.service import ConversationService
from services.messaging.service import MessagingService

@pytest_asyncio.fixture
async def test_db():
    db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with db_manager.session_factory() as session:
        yield session
    await db_manager.close()

@pytest.mark.asyncio
async def test_messaging_and_idempotency_lifecycle(test_db):
    auth_svc = AuthService(test_db)
    conv_svc = ConversationService(test_db)
    msg_svc = MessagingService(test_db)

    # 1. Setup Users
    u1, _ = await auth_svc.register(RegisterRequest(username="sender", display_name="Sender", email="sender@test.com", password="Password123!"))
    u2, _ = await auth_svc.register(RegisterRequest(username="receiver", display_name="Receiver", email="receiver@test.com", password="Password123!"))

    # 2. Create 1:1 Conversation
    conv = await conv_svc.create_or_get_direct(u1.id, u2.id)
    assert conv.id is not None
    assert conv.type == "direct"

    # 3. Send Message 1
    req1 = SendMessageRequest(
        idempotency_key="idemp-msg-001",
        conversation_id=conv.id,
        content="Hello from distributed node A",
        message_type=MessageType.TEXT
    )
    msg1 = await msg_svc.send_message(u1.id, req1, sender_device_id="dev-01")
    assert msg1.id is not None
    assert msg1.sequence_number == 1
    assert msg1.content == "Hello from distributed node A"

    # 4. Idempotency Retry Check (Client sends same key 5 times)
    msg1_retry = await msg_svc.send_message(u1.id, req1, sender_device_id="dev-01")
    assert msg1_retry.id == msg1.id  # Same exact message returned without incrementing sequence!

    # 5. Send Message 2
    req2 = SendMessageRequest(
        idempotency_key="idemp-msg-002",
        conversation_id=conv.id,
        content="Second message with monotonic ordering",
        reply_to_message_id=msg1.id
    )
    msg2 = await msg_svc.send_message(u1.id, req2)
    assert msg2.sequence_number == 2
    assert msg2.reply_to_message_id == msg1.id

    # 6. Edit Message 2
    edited = await msg_svc.edit_message(msg2.id, u1.id, EditMessageRequest(content="Edited content"))
    assert edited.is_edited is True
    assert edited.content == "Edited content"

    # 7. Add Reactions
    rx = await msg_svc.toggle_reaction(msg1.id, u2.id, "👍")
    assert "👍" in rx
    assert u2.id in rx["👍"]

    # 8. Mark Read
    read_ok = await msg_svc.mark_as_read(conv.id, u2.id, msg2.id)
    assert read_ok is True

    # 9. List Messages in Conversation
    history = await msg_svc.list_messages(conv.id)
    assert len(history) == 2
    assert history[0].sequence_number == 1
    assert history[1].sequence_number == 2

    # 10. Delete For Everyone
    del_ok = await msg_svc.delete_for_everyone(msg1.id, u1.id)
    assert del_ok is True
    del_msg = await msg_svc.get_message(msg1.id)
    assert del_msg.is_deleted_for_everyone is True
