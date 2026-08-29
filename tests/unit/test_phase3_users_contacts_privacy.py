import pytest
import pytest_asyncio
from packages.common.database import DatabaseManager, Base
from packages.contracts.auth import RegisterRequest
from packages.contracts.users import UpdateProfileRequest
from packages.contracts.contacts import AddContactRequest
from services.auth.service import AuthService
from services.users.service import UserService
from services.contacts.service import ContactService
from services.privacy.service import PrivacyService

@pytest_asyncio.fixture
async def test_db():
    db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with db_manager.session_factory() as session:
        yield session
    await db_manager.close()

@pytest.mark.asyncio
async def test_users_contacts_privacy_flow(test_db):
    auth_svc = AuthService(test_db)
    user_svc = UserService(test_db)
    contact_svc = ContactService(test_db)
    privacy_svc = PrivacyService(test_db)

    # 1. Create two users
    u1, _ = await auth_svc.register(RegisterRequest(username="alice", display_name="Alice A", email="alice@test.com", password="Password123!"))
    u2, _ = await auth_svc.register(RegisterRequest(username="bob", display_name="Bob B", email="bob@test.com", password="Password123!"))

    # 2. Update Alice Profile
    updated_profile = await user_svc.update_profile(u1.id, UpdateProfileRequest(display_name="Alice Walker", bio="Distributed engineer"))
    assert updated_profile.display_name == "Alice Walker"
    assert updated_profile.bio == "Distributed engineer"

    # 3. Search Users
    search_res = await user_svc.search_users("Alice")
    assert len(search_res) == 1
    assert search_res[0].username == "alice"

    # 4. Add Contact (Alice adds Bob)
    contact = await contact_svc.add_contact(u1.id, AddContactRequest(contact_user_id=u2.id, alias="Bobby"))
    assert contact.alias == "Bobby"
    assert contact.contact_profile.username == "bob"

    # 5. List Contacts & Toggle Favorite
    contacts = await contact_svc.list_contacts(u1.id)
    assert len(contacts) == 1
    is_fav = await contact_svc.toggle_favorite(u1.id, u2.id)
    assert is_fav is True

    # 6. Privacy: Block & Check Isolation
    assert await privacy_svc.is_blocked(u1.id, u2.id) is False
    await privacy_svc.block_user(u1.id, u2.id, reason="Spam")
    assert await privacy_svc.is_blocked(u1.id, u2.id) is True
    assert await privacy_svc.is_blocked(u2.id, u1.id) is True  # Bidirectional check

    # 7. Unblock
    await privacy_svc.unblock_user(u1.id, u2.id)
    assert await privacy_svc.is_blocked(u1.id, u2.id) is False
