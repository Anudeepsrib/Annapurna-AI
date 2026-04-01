from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from typing import AsyncGenerator
from app.core.config import settings

import os
from sqlalchemy.pool import NullPool

# Construct Async Database URL based on settings
# If DATABASE_URL is set (Production), use it.
# Otherwise, fall back to async SQLite for local dev/testing.
if settings.DATABASE_URL:
    DATABASE_URL = str(settings.DATABASE_URL)
else:
    # Use absolute path to avoid unpredicted file creation inside arbitrary terminals
    db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "annapurna.db"))
    DATABASE_URL = f"sqlite+aiosqlite:///{db_path}"

# SQLite doesn't play well with Postgres connection pools
engine_kwargs = {
    "echo": False,
    "future": True,
}

if "sqlite" in DATABASE_URL:
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs.update({
        "pool_size": 20,
        "max_overflow": 10,
        "pool_pre_ping": True
    })

# Create Async Engine
engine = create_async_engine(DATABASE_URL, **engine_kwargs)

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
