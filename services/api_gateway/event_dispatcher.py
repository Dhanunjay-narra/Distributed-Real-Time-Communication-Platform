"""Reverse Proxy and Correlation Ingress - Event Dispatcher and Message Routing Mesh.
Platform: Chatbot Distributed Real-Time Communication Platform.
"""
import asyncio, time, logging
from typing import Dict, List, Any, Optional, Callable

class ApiGatewayEventDispatcher:
    def __init__(self, service_name: str = "api_gateway"):
        self.service_name = service_name
        self.topic_subscribers: Dict[str, List[Callable]] = {}
        self.dispatch_history: List[Dict[str, Any]] = []

    def register_listener(self, topic: str, listener: Callable):
        if topic not in self.topic_subscribers:
            self.topic_subscribers[topic] = []
        self.topic_subscribers[topic].append(listener)

    async def broadcast_event(self, topic: str, payload: Dict[str, Any]) -> int:
        listeners = self.topic_subscribers.get(topic, [])
        delivered_count = 0
        timestamp = time.time()
        
        for listener in listeners:
            try:
                if asyncio.iscoroutinefunction(listener):
                    await listener(payload)
                else:
                    listener(payload)
                delivered_count += 1
            except Exception as e:
                pass

        self.dispatch_history.append({
            "topic": topic,
            "timestamp": timestamp,
            "delivered_count": delivered_count,
            "payload_size": len(payload)
        })
        if len(self.dispatch_history) > 1000:
            self.dispatch_history.pop(0)

        return delivered_count
