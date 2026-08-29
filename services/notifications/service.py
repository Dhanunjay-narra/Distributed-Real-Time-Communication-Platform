import asyncio, time
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from packages.common.logger import get_logger
from packages.events.schemas import NotificationRequestedEvent

logger = get_logger("notification-service")

class NotificationService:
    def __init__(self):
        self._sent_notifications: List[Dict[str, Any]] = []
        self._user_preferences: Dict[str, Dict[str, Any]] = {}

    async def send_push_notification(self, req: NotificationRequestedEvent) -> bool:
        prefs = self._user_preferences.get(req.recipient_id, {"enabled": True, "show_preview": True})
        if not prefs.get("enabled", True):
            logger.info(f"Notification suppressed by user preferences for recipient: {req.recipient_id}")
            return False

        payload = {
            "recipient_id": req.recipient_id,
            "title": req.title,
            "body": req.body if prefs.get("show_preview", True) else "New message received",
            "data": req.data,
            "timestamp": time.time()
        }
        self._sent_notifications.append(payload)
        logger.info(f"[PUSH SENT] Recipient: {req.recipient_id} | Title: {req.title}")
        return True

    def set_preferences(self, user_id: str, enabled: bool = True, show_preview: bool = True):
        self._user_preferences[user_id] = {"enabled": enabled, "show_preview": show_preview}

    def get_sent_notifications(self, user_id: str) -> List[Dict[str, Any]]:
        return [n for n in self._sent_notifications if n["recipient_id"] == user_id]
