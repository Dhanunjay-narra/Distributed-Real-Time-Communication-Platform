import os, sys

def w(filepath, content):
    d = os.path.dirname(filepath)
    if d:
        os.makedirs(d, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content.strip() + "\n")
    print(f"[CREATED] {filepath}")

# 1. Comprehensive End-to-End Integration Test
w("tests/e2e/__init__.py", "")

w("tests/e2e/test_complete_distributed_flow.py", """import pytest
import pytest_asyncio
from packages.common.database import DatabaseManager, Base
from packages.contracts.auth import RegisterRequest, LoginRequest
from packages.contracts.users import UpdateProfileRequest
from packages.contracts.messages import SendMessageRequest, MessageType
from packages.contracts.groups import CreateGroupRequest, GroupRole
from packages.contracts.presence import PresenceHeartbeat, PresenceStatus
from packages.contracts.sync import SyncPullRequest
from packages.contracts.media import MediaInitRequest
from packages.contracts.calls import CallSignalingDTO, CallState
from packages.contracts.moderation import CreateReportRequest, ReportReason, ApplySanctionRequest, SanctionType

from services.auth.service import AuthService
from services.users.service import UserService
from services.contacts.service import ContactService
from services.conversations.service import ConversationService
from services.messaging.service import MessagingService
from services.groups.service import GroupService
from services.presence.service import PresenceMeshService
from services.sync.service import SyncService
from services.media.service import MediaService
from services.calls.service import CallSignalingService
from services.moderation.service import ModerationService
from services.admin.service import AdminService
from services.coordination.locks import DistributedLockManager
from services.coordination.raft import RaftNode, RaftRole

@pytest_asyncio.fixture
async def e2e_db():
    db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with db_manager.session_factory() as session:
        yield session
    await db_manager.close()

@pytest.mark.asyncio
async def test_full_distributed_platform_e2e(e2e_db):
    auth_svc = AuthService(e2e_db)
    user_svc = UserService(e2e_db)
    contact_svc = ContactService(e2e_db)
    conv_svc = ConversationService(e2e_db)
    msg_svc = MessagingService(e2e_db)
    group_svc = GroupService(e2e_db)
    presence_svc = PresenceMeshService()
    sync_svc = SyncService(e2e_db)
    media_svc = MediaService(e2e_db)
    call_svc = CallSignalingService(e2e_db)
    mod_svc = ModerationService(e2e_db)
    admin_svc = AdminService(e2e_db)
    lock_mgr = DistributedLockManager("e2e-node")

    # Step 1: User Registration & Authentication
    u1, s1 = await auth_svc.register(RegisterRequest(username="alex", display_name="Alex Mercer", email="alex@test.com", password="Password123!"))
    u2, s2 = await auth_svc.register(RegisterRequest(username="maya", display_name="Maya Lin", email="maya@test.com", password="Password123!"))
    assert u1.id is not None
    assert u2.id is not None

    # Step 2: User Profiles & Social Graph
    await user_svc.update_profile(u1.id, UpdateProfileRequest(about="Building distributed real-time systems"))
    await contact_svc.add_contact(u1.id, u2.id, alias_name="Maya Architect")
    contacts = await contact_svc.list_contacts(u1.id)
    assert len(contacts) == 1
    assert contacts[0].alias_name == "Maya Architect"

    # Step 3: Direct Messaging & Idempotent Delivery
    conv = await conv_svc.create_or_get_direct(u1.id, u2.id)
    msg1 = await msg_svc.send_message(u1.id, SendMessageRequest(
        idempotency_key="e2e-idemp-1",
        conversation_id=conv.id,
        content="Welcome to the distributed real-time platform!"
    ))
    assert msg1.sequence_number == 1

    # Step 4: Real-time Presence & Typing Indicators
    await presence_svc.heartbeat(PresenceHeartbeat(user_id=u1.id, device_id="phone", status=PresenceStatus.ONLINE))
    pres_u1 = await presence_svc.get_presence(u1.id)
    assert pres_u1["is_online"] is True

    typers = await presence_svc.set_typing(conv.id, u2.id, True)
    assert u2.id in typers

    # Step 5: Group Lifecycle & Permissions
    grp = await group_svc.create_group(u1.id, CreateGroupRequest(name="Distributed Systems Engineering", member_ids=[u2.id]))
    assert grp.member_count == 2
    assert grp.owner_id == u1.id

    # Step 6: Multi-Device Sync Engine
    pull_res = await sync_svc.pull_deltas(u2.id, SyncPullRequest(device_id="laptop", since_sequence=0))
    assert len(pull_res.messages) >= 1

    # Step 7: Media Pipeline
    init_res = await media_svc.init_upload(u1.id, MediaInitRequest(filename="diagram.png", content_type="image/png", file_size_bytes=2048))
    media_dto = await media_svc.complete_upload(u1.id, init_res.media_id, "diagram.png", "image/png", 2048, width=800, height=600)
    assert media_dto.cdn_url is not None

    # Step 8: WebRTC Call Signaling
    call = await call_svc.initiate_call(caller_id=u1.id, recipient_id=u2.id, call_type="video")
    await call_svc.relay_signal(CallSignalingDTO(call_id=call.id, sender_id=u1.id, recipient_id=u2.id, type="offer", sdp="mock-sdp-data"))
    await call_svc.update_call_state(call.id, CallState.CONNECTED)
    await call_svc.update_call_state(call.id, CallState.ENDED)

    # Step 9: Safety Moderation & Reporting
    report = await mod_svc.submit_report(u2.id, CreateReportRequest(reported_user_id=u1.id, reason=ReportReason.OTHER, description="Test report"))
    assert report.status == "PENDING"

    # Step 10: Distributed Locks & Raft Engine
    lease = await lock_mgr.acquire_lock(f"conv:{conv.id}", ttl_seconds=5.0)
    assert lease is not None
    await lock_mgr.release_lock(f"conv:{conv.id}", lease)

    raft_leader = RaftNode("R1", ["R2", "R3"])
    raft_leader.start_election()
    assert raft_leader.role == RaftRole.CANDIDATE

    # Step 11: Admin Telemetry
    telemetry = await admin_svc.get_system_telemetry()
    assert telemetry["total_registered_users"] >= 2
    assert telemetry["cluster_status"] == "ONLINE"
""")

print("Phase 17 generation script complete.")
