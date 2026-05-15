import os
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel

from app.core.config import settings

DATABASE_URL = str(settings.DATABASE_URL)

if DATABASE_URL.startswith("sqlite") and ":///" in DATABASE_URL:
    db_path = DATABASE_URL.split(":///", 1)[1]
    if db_path and db_path != ":memory:":
        db_dir = os.path.dirname(os.path.abspath(db_path))
        os.makedirs(db_dir, exist_ok=True)

# SQLite doesn't play well with Postgres connection pools
engine_kwargs = {
    "echo": False,
    "future": True,
}

if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["poolclass"] = NullPool
else:
    engine_kwargs.update(
        {
            "pool_size": 20,
            "max_overflow": 10,
            "pool_pre_ping": True,
        }
    )

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
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session
