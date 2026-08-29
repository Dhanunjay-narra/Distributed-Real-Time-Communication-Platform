import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from .config import settings
from .logger import get_logger

logger = get_logger("database-manager")
Base = declarative_base()

class DatabaseManager:
    def __init__(self, database_url: str = settings.DATABASE_URL):
        self.database_url = database_url
        engine_kwargs = {"echo": False, "future": True}
        if "sqlite" not in self.database_url:
            engine_kwargs.update({"pool_size": settings.DB_POOL_SIZE, "max_overflow": settings.DB_MAX_OVERFLOW, "pool_pre_ping": True})
        self.engine = create_async_engine(self.database_url, **engine_kwargs)
        self.session_factory = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def init_models(self):
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database schemas initialized.")

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    async def close(self):
        await self.engine.dispose()

db_manager = DatabaseManager()

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_manager.get_session():
        yield session
