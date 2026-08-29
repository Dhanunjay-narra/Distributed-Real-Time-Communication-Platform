import uuid, time
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any, Set
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_, or_, desc
from packages.common.exceptions import NotFoundException, ValidationException
from packages.contracts.calls import CallSignalingDTO, CallState, CallType
from packages.events.bus import get_event_bus
from packages.events.schemas import CallSignalingEvent
from .models import CallSession

def _ensure_utc(dt: datetime) -> datetime:
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt or datetime.now(timezone.utc)

class CallSignalingService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self._rooms: Dict[str, Set[str]] = {}  # room_id -> set of user_ids

    async def initiate_call(self, caller_id: str, recipient_id: Optional[str] = None, call_type: str = "voice", room_id: Optional[str] = None) -> CallSession:
        call = CallSession(
            caller_id=caller_id,
            recipient_id=recipient_id,
            room_id=room_id or str(uuid.uuid4()),
            call_type=call_type,
            call_state=CallState.INITIATED.value
        )
        self.db.add(call)
        await self.db.commit()
        await self.db.refresh(call)

        # Track room membership
        if call.room_id not in self._rooms:
            self._rooms[call.room_id] = set()
        self._rooms[call.room_id].add(caller_id)

        # Broadcast signaling event
        bus = get_event_bus()
        await bus.publish("call.signaling", CallSignalingEvent(
            partition_key=call.id,
            call_id=call.id,
            sender_id=caller_id,
            recipient_id=recipient_id,
            signal_type="offer",
            payload={"call_type": call_type, "room_id": call.room_id}
        ))
        return call

    async def relay_signal(self, signal: CallSignalingDTO) -> bool:
        bus = get_event_bus()
        await bus.publish("call.signaling", CallSignalingEvent(
            partition_key=signal.call_id,
            call_id=signal.call_id,
            sender_id=signal.sender_id,
            recipient_id=signal.recipient_id,
            signal_type=signal.type,
            payload={"sdp": signal.sdp, "candidate": signal.candidate, "state": signal.call_state}
        ))
        return True

    async def update_call_state(self, call_id: str, new_state: CallState) -> CallSession:
        stmt = select(CallSession).where(CallSession.id == call_id)
        res = await self.db.execute(stmt)
        call = res.scalar_one_or_none()
        if not call:
            raise NotFoundException("Call session not found")

        call.call_state = new_state.value
        now = datetime.now(timezone.utc)

        if new_state == CallState.CONNECTED and not call.connected_at:
            call.connected_at = now
        elif new_state in [CallState.ENDED, CallState.REJECTED, CallState.MISSED] and not call.ended_at:
            call.ended_at = now
            if call.connected_at:
                conn_utc = _ensure_utc(call.connected_at)
                call.duration_seconds = (now - conn_utc).total_seconds()

        await self.db.commit()
        await self.db.refresh(call)
        return call

    async def list_call_history(self, user_id: str, limit: int = 50) -> List[CallSession]:
        stmt = select(CallSession).where(
            or_(CallSession.caller_id == user_id, CallSession.recipient_id == user_id)
        ).order_by(desc(CallSession.started_at)).limit(limit)
        res = await self.db.execute(stmt)
        return list(res.scalars().all())
