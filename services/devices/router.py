from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from packages.common.database import get_db_session
from packages.contracts.models import APIResponse
from packages.contracts.devices import DeviceRegisterRequest
from packages.security.jwt import decode_token
from .service import DeviceService

router = APIRouter(prefix="/api/v1/devices", tags=["Devices"])

@router.post("/{device_id}", response_model=APIResponse)
async def register_device(device_id: str, req: DeviceRegisterRequest, request: Request, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    token = authorization.replace("Bearer ", "")
    claims = decode_token(token)
    svc = DeviceService(db)
    client_ip = request.client.host if request.client else None
    dto = await svc.register_device(claims.sub, device_id, req, ip_address=client_ip)
    return APIResponse(message="Device registered", data=dto.model_dump())

@router.get("", response_model=APIResponse)
async def list_devices(authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    token = authorization.replace("Bearer ", "")
    claims = decode_token(token)
    svc = DeviceService(db)
    devices = await svc.list_user_devices(claims.sub)
    return APIResponse(data=[d.model_dump() for d in devices])

@router.delete("/{device_id}", response_model=APIResponse)
async def remove_device(device_id: str, authorization: str = Header(...), db: AsyncSession = Depends(get_db_session)):
    token = authorization.replace("Bearer ", "")
    claims = decode_token(token)
    svc = DeviceService(db)
    await svc.deactivate_device(claims.sub, device_id)
    return APIResponse(message="Device removed")
