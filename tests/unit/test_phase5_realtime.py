import pytest, asyncio
from packages.contracts.presence import PresenceStatus, PresenceHeartbeat
from services.presence.service import PresenceMeshService
from services.websocket.gateway import WebSocketGateway

@pytest.mark.asyncio
async def test_presence_mesh_lifecycle():
    svc = PresenceMeshService()
    user_id = "usr-pres-001"
    device_id = "dev-01"

    # 1. Initial State -> OFFLINE
    pres = await svc.get_presence(user_id)
    assert pres["status"] == "OFFLINE"
    assert pres["is_online"] is False

    # 2. Heartbeat -> ONLINE
    hb = PresenceHeartbeat(user_id=user_id, device_id=device_id, status=PresenceStatus.ONLINE)
    await svc.heartbeat(hb)
    pres_online = await svc.get_presence(user_id)
    assert pres_online["status"] == "ONLINE"
    assert pres_online["is_online"] is True

    # 3. Status change to AWAY
    hb_away = PresenceHeartbeat(user_id=user_id, device_id=device_id, status=PresenceStatus.AWAY)
    await svc.heartbeat(hb_away)
    pres_away = await svc.get_presence(user_id)
    assert pres_away["status"] == "AWAY"

    # 4. Device disconnect -> OFFLINE
    await svc.set_offline(user_id, device_id)
    pres_off = await svc.get_presence(user_id)
    assert pres_off["status"] == "OFFLINE"

@pytest.mark.asyncio
async def test_ephemeral_typing_indicators():
    svc = PresenceMeshService()
    conv_id = "conv-typing-001"

    # 1. User 1 starts typing
    t1 = await svc.set_typing(conv_id, "u1", True)
    assert "u1" in t1

    # 2. User 2 also starts typing (multiple participants)
    t2 = await svc.set_typing(conv_id, "u2", True)
    assert "u1" in t2
    assert "u2" in t2

    # 3. User 1 stops typing
    t3 = await svc.set_typing(conv_id, "u1", False)
    assert "u1" not in t3
    assert "u2" in t3

    # 4. Query active typers
    active = await svc.get_active_typers(conv_id)
    assert active == ["u2"]

@pytest.mark.asyncio
async def test_websocket_gateway_frame_handling():
    gw = WebSocketGateway()
    user_id = "usr-ws-001"
    device_id = "dev-ws-01"

    # 1. Ping -> Pong
    res_ping = await gw.handle_incoming_frame(user_id, device_id, '{"action": "ping"}')
    assert res_ping["action"] == "pong"

    # 2. Typing frame
    res_typing = await gw.handle_incoming_frame(user_id, device_id, '{"action": "typing", "conversation_id": "c-100", "is_typing": true}')
    assert res_typing["action"] == "typing_acknowledged"
    assert "usr-ws-001" in res_typing["active_typers"]

    # 3. Presence update frame
    res_pres = await gw.handle_incoming_frame(user_id, device_id, '{"action": "presence_update", "status": "DND"}')
    assert res_pres["action"] == "presence_acknowledged"
    assert res_pres["status"] == "DND"
