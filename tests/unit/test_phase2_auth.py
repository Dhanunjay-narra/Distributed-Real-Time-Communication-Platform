import pytest
import pytest_asyncio
from packages.common.database import DatabaseManager, Base
from packages.contracts.auth import RegisterRequest, LoginRequest, OTPRequest, OTPVerifyRequest
from packages.contracts.devices import DeviceRegisterRequest
from services.auth.service import AuthService
from services.devices.service import DeviceService
from packages.common.exceptions import ConflictException, UnauthorizedException

@pytest_asyncio.fixture
async def test_db():
    db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with db_manager.session_factory() as session:
        yield session
    await db_manager.close()

@pytest.mark.asyncio
async def test_registration_and_login_flow(test_db):
    auth_svc = AuthService(test_db)
    
    # 1. Register User
    reg_req = RegisterRequest(
        username="dhanunjay",
        display_name="Dhanunjay Narra",
        email="dhanunjay@example.com",
        password="SecureDistributedPassword2026!",
        device_name="MacBook Pro M3",
        device_type="desktop"
    )
    user, tokens = await auth_svc.register(reg_req, ip_address="192.168.1.100")
    assert user.id is not None
    assert user.username == "dhanunjay"
    assert tokens.access_token is not None
    assert tokens.refresh_token is not None

    # 2. Duplicate registration rejected
    with pytest.raises(ConflictException):
        await auth_svc.register(reg_req)

    # 3. Successful Login
    login_req = LoginRequest(
        identifier="dhanunjay@example.com",
        password="SecureDistributedPassword2026!",
        device_name="iPhone 15 Pro",
        device_type="ios"
    )
    user_login, login_tokens = await auth_svc.login(login_req, ip_address="192.168.1.101")
    assert user_login.id == user.id
    assert login_tokens.access_token is not None

    # 4. Failed Login with invalid password
    with pytest.raises(UnauthorizedException):
        await auth_svc.login(LoginRequest(identifier="dhanunjay", password="WrongPassword!"))

    # 5. Token Refresh Rotation
    new_tokens = await auth_svc.refresh_tokens(login_tokens.refresh_token, device_id=login_tokens.device_id)
    assert new_tokens.access_token is not None
    assert new_tokens.refresh_token != login_tokens.refresh_token

    # 6. Session Management
    sessions = await auth_svc.list_sessions(user.id)
    assert len(sessions) >= 2

    # 7. Device Service Registration
    device_svc = DeviceService(test_db)
    dev_dto = await device_svc.register_device(
        user_id=user.id,
        device_id="dev-tablet-01",
        req=DeviceRegisterRequest(device_name="iPad Air", device_type="tablet", push_token="push_tok_xyz123")
    )
    assert dev_dto.device_name == "iPad Air"
    devices = await device_svc.list_user_devices(user.id)
    assert len(devices) >= 2

@pytest.mark.asyncio
async def test_otp_flow(test_db):
    auth_svc = AuthService(test_db)
    otp_req = OTPRequest(target="user@example.com", channel="email")
    code = await auth_svc.generate_otp(otp_req)
    assert len(code) == 6

    # Verify OTP
    verify_req = OTPVerifyRequest(target="user@example.com", code=code)
    verified = await auth_svc.verify_otp(verify_req)
    assert verified is True
