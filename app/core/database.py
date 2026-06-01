from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from app.core.config import settings
from app.core.logging import log

# Create async engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,           # Ensures connections are alive
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
)

# Async session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

async def get_db() -> AsyncSession:
    """Dependency for FastAPI to get DB session"""
    async with AsyncSessionLocal() as session:
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