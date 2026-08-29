import pytest
import pytest_asyncio
from packages.common.database import DatabaseManager, Base
from packages.contracts.auth import RegisterRequest
from packages.contracts.media import MediaInitRequest
from services.auth.service import AuthService
from services.media.service import MediaService
from packages.common.exceptions import ValidationException

@pytest_asyncio.fixture
async def test_db():
    db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with db_manager.session_factory() as session:
        yield session
    await db_manager.close()

@pytest.mark.asyncio
async def test_media_pipeline_and_validation(test_db):
    auth_svc = AuthService(test_db)
    media_svc = MediaService(test_db)

    user, _ = await auth_svc.register(RegisterRequest(username="media_user", display_name="Media User", email="media@test.com", password="Password123!"))

    # 1. Prohibited extension blocked
    with pytest.raises(ValidationException):
        await media_svc.init_upload(user.id, MediaInitRequest(
            filename="malicious_payload.exe",
            content_type="application/x-msdownload",
            file_size_bytes=1024,
            media_category="document"
        ))

    # 2. Init Image Upload
    req = MediaInitRequest(
        filename="architecture_diagram.png",
        content_type="image/png",
        file_size_bytes=4 * 1024 * 1024,
        media_category="image"
    )
    init_res = await media_svc.init_upload(user.id, req)
    assert init_res.media_id is not None
    assert init_res.total_chunks == 1

    # 3. Complete Upload
    media_dto = await media_svc.complete_upload(
        user_id=user.id,
        media_id=init_res.media_id,
        filename="architecture_diagram.png",
        content_type="image/png",
        file_size_bytes=4 * 1024 * 1024,
        width=1920,
        height=1080
    )
    assert media_dto.cdn_url is not None
    assert media_dto.thumbnail_url is not None
    assert media_dto.width == 1920

    # 4. Query Media Details
    retrieved = await media_svc.get_media(init_res.media_id)
    assert retrieved.filename == "architecture_diagram.png"
    assert retrieved.file_size_bytes == 4 * 1024 * 1024
