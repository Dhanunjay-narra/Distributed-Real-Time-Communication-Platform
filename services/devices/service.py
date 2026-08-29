from datetime import datetime, timezone
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from packages.common.exceptions import NotFoundException
from services.auth.models import Device
from packages.contracts.devices import DeviceRegisterRequest, DeviceDTO

def _ensure_utc(dt: datetime) -> datetime:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt or datetime.now(timezone.utc)

class DeviceService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def register_device(self, user_id: str, device_id: str, req: DeviceRegisterRequest, ip_address: Optional[str] = None) -> DeviceDTO:
        stmt = select(Device).where(and_(Device.user_id == user_id, Device.device_id == device_id))
        res = await self.db.execute(stmt)
        device = res.scalar_one_or_none()

        now = datetime.now(timezone.utc)
        if not device:
            device = Device(
                user_id=user_id,
                device_id=device_id,
                device_name=req.device_name,
                device_type=req.device_type,
                push_token=req.push_token,
                app_version=getattr(req, "app_version", "1.0.0"),
                os_version=getattr(req, "os_version", None),
                last_ip=ip_address,
                last_active=now,
                is_active=True
            )
            self.db.add(device)
        else:
            device.device_name = req.device_name
            device.device_type = req.device_type
            if req.push_token: device.push_token = req.push_token
            device.last_ip = ip_address
            device.last_active = now
            device.is_active = True

        await self.db.commit()
        await self.db.refresh(device)
        return DeviceDTO(
            id=device.id,
            user_id=device.user_id,
            device_id=device.device_id,
            device_name=device.device_name,
            device_type=device.device_type,
            push_token=device.push_token,
            last_ip=device.last_ip,
            last_active=_ensure_utc(device.last_active),
            is_active=device.is_active,
            created_at=_ensure_utc(device.created_at),
            updated_at=_ensure_utc(device.last_active)
        )

    async def list_user_devices(self, user_id: str) -> List[DeviceDTO]:
        stmt = select(Device).where(and_(Device.user_id == user_id, Device.is_active == True))
        res = await self.db.execute(stmt)
        devices = res.scalars().all()
        return [
            DeviceDTO(
                id=d.id,
                user_id=d.user_id,
                device_id=d.device_id,
                device_name=d.device_name,
                device_type=d.device_type,
                push_token=d.push_token,
                last_ip=d.last_ip,
                last_active=_ensure_utc(d.last_active),
                is_active=d.is_active,
                created_at=_ensure_utc(d.created_at),
                updated_at=_ensure_utc(d.last_active)
            ) for d in devices
        ]

    async def deactivate_device(self, user_id: str, device_id: str) -> bool:
        stmt = update(Device).where(and_(Device.user_id == user_id, Device.device_id == device_id)).values(is_active=False)
        await self.db.execute(stmt)
        await self.db.commit()
        return True
