from typing import Optional, List
from datetime import datetime
from enum import Enum
from pydantic import Field
from .models import TimestampedModel, BaseDTO
from .users import UserProfileDTO

class GroupRole(str, Enum):
    OWNER = "owner"
    ADMIN = "admin"
    MODERATOR = "moderator"
    MEMBER = "member"

class CreateGroupRequest(BaseDTO):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    member_ids: List[str] = []
    announcement_only: bool = False

class UpdateGroupMemberRoleRequest(BaseDTO):
    new_role: GroupRole

class GroupMemberDTO(TimestampedModel):
    group_id: str
    user_id: str
    role: GroupRole = GroupRole.MEMBER
    joined_at: datetime
    profile: Optional[UserProfileDTO] = None

class GroupDTO(TimestampedModel):
    conversation_id: str
    name: str
    description: Optional[str] = None
    avatar_url: Optional[str] = None
    owner_id: str
    member_count: int = 0
    announcement_only: bool = False
    invite_code: Optional[str] = None
    members: List[GroupMemberDTO] = []
