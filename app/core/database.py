from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.core.config import settings
from app.core.logging import log

# Lazy-initialized async engine and sessionmaker to avoid creating
# async IO objects at import time (which can trigger greenlet/asyncpg errors
# when code is imported in a sync context such as Alembic).
_async_engine = None
_async_sessionmaker = None

def get_async_engine():
    global _async_engine
    if _async_engine is None:
        _async_engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            pool_pre_ping=True,
            pool_size=10,
            max_overflow=20,
            pool_timeout=30,
        )
    return _async_engine

def get_async_sessionmaker():
    global _async_sessionmaker
    if _async_sessionmaker is None:
        _async_sessionmaker = async_sessionmaker(
            bind=get_async_engine(),
            expire_on_commit=False,
            autoflush=False,
            autocommit=False,
        )
    return _async_sessionmaker


async def get_db() -> AsyncSession:
    """Dependency for FastAPI to get DB session"""
    sessionmaker = get_async_sessionmaker()
    async with sessionmaker() as session:
        try:
            yield session
        except Exception as e:
            log.error(f"Database error: {str(e)}")
            await session.rollback()
            raise
        finally:
            await session.close()


# For Alembic migrations (sync context)
from sqlalchemy import create_engine

def get_sync_engine():
    """Used by Alembic"""
    # Convert async URL to sync URL
    sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg://")
    return create_engine(sync_url, echo=False)