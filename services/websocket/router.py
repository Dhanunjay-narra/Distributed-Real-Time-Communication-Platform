import time
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, Depends, Header
from packages.security.jwt import decode_token
from packages.contracts.models import APIResponse
from .gateway import gateway_instance
from services.presence.service import PresenceMeshService

router = APIRouter(tags=["Real-Time Gateway"])
presence_svc = gateway_instance.presence_svc

@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    device_id: str = Query(default="web-client")
):
    try:
        claims = decode_token(token)
    except Exception:
        await websocket.close(code=4001, reason="Unauthorized")
        return

    user_id = claims.sub
    await gateway_instance.connect(websocket, user_id, device_id)
    try:
        while True:
            raw_text = await websocket.receive_text()
            response = await gateway_instance.handle_incoming_frame(user_id, device_id, raw_text)
            if response:
                await websocket.send_json(response)
    except WebSocketDisconnect:
        await gateway_instance.disconnect(user_id, device_id)
    except Exception:
        await gateway_instance.disconnect(user_id, device_id)

@router.get("/api/v1/presence/{user_id}", response_model=APIResponse)
async def get_user_presence(user_id: str):
    pres = await presence_svc.get_presence(user_id)
    return APIResponse(data=pres)

@router.get("/api/v1/typing/{conversation_id}", response_model=APIResponse)
async def get_active_typers(conversation_id: str):
    typers = await presence_svc.get_active_typers(conversation_id)
    return APIResponse(data={"conversation_id": conversation_id, "active_typers": typers})
