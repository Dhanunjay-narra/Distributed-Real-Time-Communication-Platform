import secrets, uuid
from datetime import datetime, timezone
from typing import List, Optional, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_
from packages.common.exceptions import NotFoundException, ForbiddenException, ConflictException, ValidationException
from packages.contracts.groups import CreateGroupRequest, GroupDTO, GroupMemberDTO, GroupRole
from services.auth.models import User
from services.conversations.models import Conversation, ConversationParticipant
from services.users.service import UserService
from .models import Group, GroupMember
from packages.events.bus import get_event_bus
from packages.events.schemas import GroupCreatedEvent, MemberAddedEvent

def _ensure_utc(dt: datetime) -> datetime:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt or datetime.now(timezone.utc)

class GroupService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_svc = UserService(db)

    async def create_group(self, owner_id: str, req: CreateGroupRequest) -> GroupDTO:
        # 1. Create underlying conversation container
        conv = Conversation(
            type="group",
            title=req.name,
            avatar_url=req.avatar_url,
            created_by=owner_id,
            sequence_counter=0
        )
        self.db.add(conv)
        await self.db.flush()

        # 2. Create Group record
        invite_code = secrets.token_urlsafe(16)
        group = Group(
            conversation_id=conv.id,
            name=req.name,
            description=req.description,
            avatar_url=req.avatar_url,
            owner_id=owner_id,
            announcement_only=req.announcement_only,
            invite_code=invite_code
        )
        self.db.add(group)
        await self.db.flush()

        # 3. Add Owner as first member
        owner_member = GroupMember(group_id=group.id, user_id=owner_id, role=GroupRole.OWNER.value)
        owner_p = ConversationParticipant(conversation_id=conv.id, user_id=owner_id, role="owner")
        self.db.add_all([owner_member, owner_p])

        # 4. Add initial members
        initial_member_ids = list(set(req.member_ids) - {owner_id})
        for mid in initial_member_ids:
            gm = GroupMember(group_id=group.id, user_id=mid, role=GroupRole.MEMBER.value)
            cp = ConversationParticipant(conversation_id=conv.id, user_id=mid, role="member")
            self.db.add_all([gm, cp])

        await self.db.commit()
        await self.db.refresh(group)

        # Publish group event
        bus = get_event_bus()
        await bus.publish("group.events", GroupCreatedEvent(
            partition_key=group.id,
            group_id=group.id,
            conversation_id=conv.id,
            name=group.name,
            creator_id=owner_id,
            member_ids=[owner_id] + initial_member_ids
        ))

        return await self.get_group(group.id, owner_id)

    async def get_group(self, group_id: str, requester_id: str) -> GroupDTO:
        stmt = select(Group).where(Group.id == group_id)
        res = await self.db.execute(stmt)
        group = res.scalar_one_or_none()
        if not group:
            raise NotFoundException("Group not found")

        # Load members
        stmt_m = select(GroupMember).where(GroupMember.group_id == group_id)
        res_m = await self.db.execute(stmt_m)
        members = res_m.scalars().all()

        member_dtos = []
        for m in members:
            profile = await self.user_svc.get_profile(m.user_id)
            member_dtos.append(GroupMemberDTO(
                id=m.id,
                group_id=m.group_id,
                user_id=m.user_id,
                role=GroupRole(m.role),
                joined_at=_ensure_utc(m.joined_at),
                profile=profile,
                created_at=_ensure_utc(m.joined_at),
                updated_at=_ensure_utc(m.joined_at)
            ))

        return GroupDTO(
            id=group.id,
            conversation_id=group.conversation_id,
            name=group.name,
            description=group.description,
            avatar_url=group.avatar_url,
            owner_id=group.owner_id,
            member_count=len(members),
            announcement_only=group.announcement_only,
            invite_code=group.invite_code,
            members=member_dtos,
            created_at=_ensure_utc(group.created_at),
            updated_at=_ensure_utc(group.updated_at)
        )

    async def add_member(self, group_id: str, requester_id: str, new_user_id: str) -> bool:
        group = await self._get_group_entity(group_id)
        requester_role = await self._get_member_role(group_id, requester_id)
        if requester_role not in [GroupRole.OWNER, GroupRole.ADMIN]:
            raise ForbiddenException("Only Group Admins or Owner can add members")

        existing_role = await self._get_member_role(group_id, new_user_id)
        if existing_role:
            return True

        gm = GroupMember(group_id=group.id, user_id=new_user_id, role=GroupRole.MEMBER.value)
        cp = ConversationParticipant(conversation_id=group.conversation_id, user_id=new_user_id, role="member")
        self.db.add_all([gm, cp])
        await self.db.commit()

        bus = get_event_bus()
        await bus.publish("group.events", MemberAddedEvent(
            partition_key=group.id,
            group_id=group.id,
            conversation_id=group.conversation_id,
            user_id=new_user_id,
            added_by=requester_id
        ))
        return True

    async def remove_member(self, group_id: str, requester_id: str, target_user_id: str) -> bool:
        group = await self._get_group_entity(group_id)
        requester_role = await self._get_member_role(group_id, requester_id)
        target_role = await self._get_member_role(group_id, target_user_id)

        if not target_role:
            return True

        # Allow user to leave voluntarily or admin/owner removal
        is_self_leave = (requester_id == target_user_id)
        if not is_self_leave:
            if requester_role not in [GroupRole.OWNER, GroupRole.ADMIN]:
                raise ForbiddenException("Only admins can remove members")
            if target_role == GroupRole.OWNER:
                raise ForbiddenException("Cannot remove the group owner")
            if requester_role == GroupRole.ADMIN and target_role == GroupRole.ADMIN:
                raise ForbiddenException("Admins cannot remove fellow admins")

        # Delete memberships
        await self.db.execute(delete(GroupMember).where(and_(GroupMember.group_id == group.id, GroupMember.user_id == target_user_id)))
        await self.db.execute(delete(ConversationParticipant).where(and_(ConversationParticipant.conversation_id == group.conversation_id, ConversationParticipant.user_id == target_user_id)))
        await self.db.commit()
        return True

    async def update_member_role(self, group_id: str, requester_id: str, target_user_id: str, new_role: GroupRole) -> bool:
        requester_role = await self._get_member_role(group_id, requester_id)
        if requester_role != GroupRole.OWNER:
            raise ForbiddenException("Only group owner can change member roles")

        stmt = update(GroupMember).where(and_(GroupMember.group_id == group_id, GroupMember.user_id == target_user_id)).values(role=new_role.value)
        await self.db.execute(stmt)
        await self.db.commit()
        return True

    async def join_by_invite(self, invite_code: str, user_id: str) -> GroupDTO:
        stmt = select(Group).where(Group.invite_code == invite_code)
        res = await self.db.execute(stmt)
        group = res.scalar_one_or_none()
        if not group:
            raise NotFoundException("Invalid or expired invite code")

        existing_role = await self._get_member_role(group.id, user_id)
        if not existing_role:
            gm = GroupMember(group_id=group.id, user_id=user_id, role=GroupRole.MEMBER.value)
            cp = ConversationParticipant(conversation_id=group.conversation_id, user_id=user_id, role="member")
            self.db.add_all([gm, cp])
            await self.db.commit()

        return await self.get_group(group.id, user_id)

    async def _get_group_entity(self, group_id: str) -> Group:
        stmt = select(Group).where(Group.id == group_id)
        res = await self.db.execute(stmt)
        group = res.scalar_one_or_none()
        if not group: raise NotFoundException("Group not found")
        return group

    async def _get_member_role(self, group_id: str, user_id: str) -> Optional[GroupRole]:
        stmt = select(GroupMember.role).where(and_(GroupMember.group_id == group_id, GroupMember.user_id == user_id))
        res = await self.db.execute(stmt)
        role_str = res.scalar_one_or_none()
        return GroupRole(role_str) if role_str else None
