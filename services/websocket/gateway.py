import json, asyncio, time
from typing import Dict, Set, Optional, Any, Callable, List
from fastapi import WebSocket, WebSocketDisconnect
from packages.common.logger import get_logger
from packages.security.jwt import decode_token
from services.presence.service import PresenceMeshService
from packages.contracts.presence import PresenceHeartbeat, PresenceStatus

logger = get_logger("websocket-gateway")

class WebSocketGateway:
    def __init__(self):
        self._connections: Dict[str, Dict[str, WebSocket]] = {}
        self._conversation_subs: Dict[str, Set[str]] = {}
        self.presence_svc = PresenceMeshService()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, user_id: str, device_id: str):
        await websocket.accept()
        async with self._lock:
            if user_id not in self._connections:
                self._connections[user_id] = {}
            self._connections[user_id][device_id] = websocket

        logger.info(f"WebSocket client connected: user={user_id}, device={device_id}")
        await self.presence_svc.heartbeat(PresenceHeartbeat(
            user_id=user_id,
            device_id=device_id,
            status=PresenceStatus.ONLINE
        ))

    async def disconnect(self, user_id: str, device_id: str):
        async with self._lock:
            if user_id in self._connections:
                self._connections[user_id].pop(device_id, None)
                if not self._connections[user_id]:
                    del self._connections[user_id]

        logger.info(f"WebSocket client disconnected: user={user_id}, device={device_id}")
        await self.presence_svc.set_offline(user_id, device_id)

    async def send_to_device(self, user_id: str, device_id: str, payload: Dict[str, Any]) -> bool:
        async with self._lock:
            ws = self._connections.get(user_id, {}).get(device_id)
            if ws:
                try:
                    await ws.send_text(json.dumps(payload))
                    return True
                except Exception as e:
                    logger.warning(f"Failed sending to device {device_id}: {e}")
        return False

    async def send_to_user(self, user_id: str, payload: Dict[str, Any]) -> int:
        count = 0
        async with self._lock:
            devices = dict(self._connections.get(user_id, {}))
        for dev_id, ws in devices.items():
            try:
                await ws.send_text(json.dumps(payload))
                count += 1
            except Exception as e:
                logger.warning(f"Error sending to user {user_id} device {dev_id}: {e}")
        return count

    async def broadcast_to_users(self, user_ids: List[str], payload: Dict[str, Any]):
        tasks = [self.send_to_user(uid, payload) for uid in user_ids]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def handle_incoming_frame(self, user_id: str, device_id: str, raw_message: str) -> Optional[Dict[str, Any]]:
        try:
            data = json.loads(raw_message)
            action = data.get("action", "").lower()

            if action == "ping":
                await self.presence_svc.heartbeat(PresenceHeartbeat(
                    user_id=user_id,
                    device_id=device_id,
                    status=PresenceStatus.ONLINE
                ))
                return {"action": "pong", "timestamp": time.time()}

            elif action == "typing":
                conv_id = data.get("conversation_id")
                is_typing = data.get("is_typing", True)
                if conv_id:
                    active = await self.presence_svc.set_typing(conv_id, user_id, is_typing)
                    return {"action": "typing_acknowledged", "conversation_id": conv_id, "active_typers": active}

            elif action == "presence_update":
                status_str = data.get("status", "ONLINE")
                await self.presence_svc.heartbeat(PresenceHeartbeat(
                    user_id=user_id,
                    device_id=device_id,
                    status=PresenceStatus(status_str),
                    custom_status=data.get("custom_status")
                ))
                return {"action": "presence_acknowledged", "status": status_str}

            return {"action": "acknowledged", "received": data}
        except Exception as e:
            logger.error(f"Error processing frame from user {user_id}: {e}")
            return {"action": "error", "message": str(e)}

gateway_instance = WebSocketGateway()
