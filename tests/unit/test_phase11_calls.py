import pytest
import pytest_asyncio
from packages.common.database import DatabaseManager, Base
from packages.contracts.auth import RegisterRequest
from packages.contracts.calls import CallSignalingDTO, CallState
from services.auth.service import AuthService
from services.calls.service import CallSignalingService

@pytest_asyncio.fixture
async def test_db():
    db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with db_manager.session_factory() as session:
        yield session
    await db_manager.close()

@pytest.mark.asyncio
async def test_webrtc_call_lifecycle_and_signaling(test_db):
    auth_svc = AuthService(test_db)
    call_svc = CallSignalingService(test_db)

    caller, _ = await auth_svc.register(RegisterRequest(username="caller_1", display_name="Caller", email="caller@test.com", password="Password123!"))
    callee, _ = await auth_svc.register(RegisterRequest(username="callee_1", display_name="Callee", email="callee@test.com", password="Password123!"))

    # 1. Initiate 1:1 Video Call
    call = await call_svc.initiate_call(caller_id=caller.id, recipient_id=callee.id, call_type="video")
    assert call.id is not None
    assert call.call_state == "initiated"
    assert call.call_type == "video"

    # 2. Relay SDP Offer & Answer Signals
    signal_offer = CallSignalingDTO(call_id=call.id, sender_id=caller.id, recipient_id=callee.id, type="offer", sdp="v=0;o=alice;s=session...")
    relayed_offer = await call_svc.relay_signal(signal_offer)
    assert relayed_offer is True

    signal_answer = CallSignalingDTO(call_id=call.id, sender_id=callee.id, recipient_id=caller.id, type="answer", sdp="v=0;o=bob;s=session...")
    relayed_answer = await call_svc.relay_signal(signal_answer)
    assert relayed_answer is True

    # 3. Transition state to CONNECTED
    connected_call = await call_svc.update_call_state(call.id, CallState.CONNECTED)
    assert connected_call.call_state == "connected"
    assert connected_call.connected_at is not None

    # 4. End Call and Calculate Duration
    ended_call = await call_svc.update_call_state(call.id, CallState.ENDED)
    assert ended_call.call_state == "ended"
    assert ended_call.ended_at is not None
    assert ended_call.duration_seconds >= 0.0

    # 5. Check Call History
    history = await call_svc.list_call_history(caller.id)
    assert len(history) == 1
    assert history[0].id == call.id
