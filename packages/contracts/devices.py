from typing import Optional
from datetime import datetime
from .models import TimestampedModel, BaseDTO

class DeviceRegisterRequest(BaseDTO):
    device_name: str
    device_type: str
    push_token: Optional[str] = None

class DeviceDTO(TimestampedModel):
    user_id: str
    device_id: str
    device_name: str
    device_type: str
    push_token: Optional[str] = None
    last_active: datetime
    is_active: bool = True
