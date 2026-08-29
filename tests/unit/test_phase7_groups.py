import pytest
import pytest_asyncio
from packages.common.database import DatabaseManager, Base
from packages.contracts.auth import RegisterRequest
from packages.contracts.groups import CreateGroupRequest, GroupRole
from services.auth.service import AuthService
from services.groups.service import GroupService
from packages.common.exceptions import ForbiddenException, NotFoundException

@pytest_asyncio.fixture
async def test_db():
    db_manager = DatabaseManager("sqlite+aiosqlite:///:memory:")
    async with db_manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with db_manager.session_factory() as session:
        yield session
    await db_manager.close()

@pytest.mark.asyncio
async def test_group_lifecycle_and_rbac(test_db):
    auth_svc = AuthService(test_db)
    group_svc = GroupService(test_db)

    # 1. Setup Users
    owner, _ = await auth_svc.register(RegisterRequest(username="owner", display_name="Group Owner", email="owner@test.com", password="Password123!"))
    alice, _ = await auth_svc.register(RegisterRequest(username="alice", display_name="Alice", email="alice@test.com", password="Password123!"))
    bob, _ = await auth_svc.register(RegisterRequest(username="bob", display_name="Bob", email="bob@test.com", password="Password123!"))

    # 2. Create Group
    req = CreateGroupRequest(
        name="Architecture Core Team",
        description="Distributed systems development group",
        member_ids=[alice.id]
    )
    group = await group_svc.create_group(owner.id, req)
    assert group.name == "Architecture Core Team"
    assert group.owner_id == owner.id
    assert group.member_count == 2
    assert group.invite_code is not None

    # 3. Add Member (Bob) by Owner
    add_ok = await group_svc.add_member(group.id, owner.id, bob.id)
    assert add_ok is True
    updated_grp = await group_svc.get_group(group.id, owner.id)
    assert updated_grp.member_count == 3

    # 4. Promote Alice to Admin
    role_ok = await group_svc.update_member_role(group.id, owner.id, alice.id, GroupRole.ADMIN)
    assert role_ok is True

    # 5. Non-Owner cannot change roles (Alice tries to promote Bob -> Forbidden)
    with pytest.raises(ForbiddenException):
        await group_svc.update_member_role(group.id, alice.id, bob.id, GroupRole.ADMIN)

    # 6. Join by Invite code (New user Charlie)
    charlie, _ = await auth_svc.register(RegisterRequest(username="charlie", display_name="Charlie", email="charlie@test.com", password="Password123!"))
    joined = await group_svc.join_by_invite(group.invite_code, charlie.id)
    assert joined.member_count == 4

    # 7. Remove Member
    rem_ok = await group_svc.remove_member(group.id, owner.id, charlie.id)
    assert rem_ok is True
    post_rem = await group_svc.get_group(group.id, owner.id)
    assert post_rem.member_count == 3
