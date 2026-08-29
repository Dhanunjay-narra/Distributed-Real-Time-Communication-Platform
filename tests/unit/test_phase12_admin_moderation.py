import pytest
import pytest_asyncio
from packages.common.database import DatabaseManager, Base
from packages.contracts.auth import RegisterRequest
from packages.contracts.moderation import CreateReportRequest, ReportReason, ApplySanctionRequest, SanctionType
from services.auth.service import AuthService
from services.moderation.service import ModerationService
from services.analytics.service import analytics_engine
from services.admin.service import AdminService

@pytest_asyncio.fixture
async def test_db():
    db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with db_manager.session_factory() as session:
        yield session
    await db_manager.close()

@pytest.mark.asyncio
async def test_safety_moderation_and_admin_telemetry(test_db):
    auth_svc = AuthService(test_db)
    mod_svc = ModerationService(test_db)
    admin_svc = AdminService(test_db)

    u1, _ = await auth_svc.register(RegisterRequest(username="admin_user", display_name="Admin", email="admin@test.com", password="Password123!"))
    u2, _ = await auth_svc.register(RegisterRequest(username="spammer_user", display_name="Spammer", email="spammer@test.com", password="Password123!"))

    # 1. Automated Content Scanner
    assert mod_svc.scan_content("Hey, how is your project going?") is False
    assert mod_svc.scan_content("Click here for free_gift_cards now!") is True

    # 2. Submit Content Report
    report = await mod_svc.submit_report(u1.id, CreateReportRequest(
        reported_user_id=u2.id,
        reason=ReportReason.SPAM,
        description="User is broadcasting spam links"
    ))
    assert report.id is not None
    assert report.status == "PENDING"

    # 3. Apply Sanction (Temporary Ban)
    sanction = await mod_svc.apply_sanction(ApplySanctionRequest(
        user_id=u2.id,
        sanction_type=SanctionType.TEMPORARY_BAN,
        duration_hours=24,
        reason="Automated spam detection"
    ))
    assert sanction.id is not None
    assert await mod_svc.is_user_banned(u2.id) is True

    # 4. Analytics Engine
    analytics_engine.record_message(u1.id, latency_ms=12.5)
    analytics_engine.record_message(u2.id, latency_ms=16.0)

    # 5. Admin System Telemetry
    telemetry = await admin_svc.get_system_telemetry()
    assert telemetry["total_registered_users"] >= 2
    assert telemetry["pending_reports_queue"] >= 1
    assert telemetry["cluster_status"] == "ONLINE"
