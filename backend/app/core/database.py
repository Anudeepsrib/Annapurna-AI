from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.core.config import settings

# Construct Async Database URL based on settings
# If DATABASE_URL is set (Production), use it.
# Otherwise, fall back to async SQLite for local dev/testing.
if settings.DATABASE_URL:
    DATABASE_URL = str(settings.DATABASE_URL)
else:
    DATABASE_URL = "sqlite+aiosqlite:///./annapurna.db"

# Create Async Engine
# echo=True logs SQL queries (good for debugging, disable in prod if noisy)
engine = create_async_engine(
    DATABASE_URL, 
    echo=False, 
    future=True,
    # Connection Pool Settings (Relevant for Postgres)
    pool_size=20,     # Max persistent connections
    max_overflow=10,  # Max additional connections during spikes
    pool_pre_ping=True # Check connection health before usage
)

async def create_db_and_tables():
    """
    Create tables if they don't exist.
    """
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency to provide an Async DB session per request.
    """
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    async with async_session() as session:
        yield session
