import uuid
from datetime import datetime, timezone
from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, ConfigDict

class BaseDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class UUIDModel(BaseDTO):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

class TimestampedModel(UUIDModel):
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class APIResponse(BaseDTO):
    success: bool = True
    message: Optional[str] = None
    data: Optional[Any] = None
    metadata: Optional[Dict[str, Any]] = None
