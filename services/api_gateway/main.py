import time
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from packages.common.config import settings
from .middleware import GatewayMiddleware

from services.auth.router import router as auth_router
from services.devices.router import router as device_router
from services.users.router import router as user_router
from services.contacts.router import router as contact_router
from services.privacy.router import router as privacy_router
from services.conversations.router import router as conversation_router
from services.messaging.router import router as message_router
from services.groups.router import router as group_router
from services.websocket.router import router as ws_router
from services.sync.router import router as sync_router
from services.media.router import router as media_router

app = FastAPI(
    title="Chatbot Distributed API Gateway",
    version="1.0.0",
    description="Unified API Gateway and Reverse Proxy for Distributed Chatbot Platform"
)

app.add_middleware(GatewayMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(device_router)
app.include_router(user_router)
app.include_router(contact_router)
app.include_router(privacy_router)
app.include_router(conversation_router)
app.include_router(message_router)
app.include_router(group_router)
app.include_router(ws_router)
app.include_router(sync_router)
app.include_router(media_router)

@app.get("/health")
async def health():
    return {
        "service": "api-gateway",
        "status": "healthy",
        "timestamp": time.time(),
        "routes": len(app.routes)
    }
