import asyncio
from typing import AsyncGenerator, Optional
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncEngine
from sqlalchemy.orm import declarative_base
from .config import settings
from .logger import get_logger

logger = get_logger("database-manager")
Base = declarative_base()

class DatabaseManager:
    def __init__(self, db_url: str = settings.DATABASE_URL, replica_url: Optional[str] = settings.DATABASE_REPLICA_URL):
        self.db_url = db_url
        self.replica_url = replica_url
        is_sqlite = db_url.startswith("sqlite")
        
        if is_sqlite:
            self.engine: AsyncEngine = create_async_engine(db_url, echo=settings.DB_ECHO, future=True)
        else:
            self.engine: AsyncEngine = create_async_engine(
                db_url,
                echo=settings.DB_ECHO,
                pool_size=settings.DB_POOL_SIZE,
                max_overflow=settings.DB_MAX_OVERFLOW,
                pool_timeout=settings.DB_POOL_TIMEOUT,
                pool_recycle=settings.DB_POOL_RECYCLE,
                pool_pre_ping=True,
                future=True
            )
        self.session_factory = async_sessionmaker(bind=self.engine, class_=AsyncSession, expire_on_commit=False)

    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception as e:
                await session.rollback()
                logger.error(f"Database session rolled back due to exception: {e}")
                raise
            finally:
                await session.close()

    async def check_health(self) -> bool:
        try:
            async with self.engine.connect() as conn:
                await conn.execute("SELECT 1")
            return True
        except Exception:
            return False

    async def close(self):
        await self.engine.dispose()

db_manager = DatabaseManager()
async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async for session in db_manager.get_session():
        yield session
