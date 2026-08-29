"""Ephemeral Mesh and Activity Streams - Domain Entities and State Models.
Platform: Chatbot Distributed Real-Time Communication Platform.
"""
import uuid, time
from datetime import datetime, timezone
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class PresenceDomainEntity(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = "presence"
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True
    tenant_id: str = "default"

    def touch(self) -> None:
        self.updated_at = datetime.now(timezone.utc)
        self.version += 1

    def to_payload(self) -> Dict[str, Any]:
        return self.model_dump(mode="json")
