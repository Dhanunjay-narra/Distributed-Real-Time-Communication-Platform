from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from packages.common.config import settings
from packages.common.database import db_manager
from .router import router as auth_router
from services.devices.router import router as device_router

app = FastAPI(title="Chatbot Identity & Device Service", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(device_router)

@app.on_event("startup")
async def startup():
    await db_manager.init_models()

@app.get("/health")
async def health():
    return {"service": "auth-service", "status": "healthy"}
