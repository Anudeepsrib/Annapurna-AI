import asyncio
import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///:memory:")

from app.core.database import get_session  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture(name="client")
def client_fixture():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async def init_db():
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def get_session_override():
        async with async_session() as session:
            yield session

    asyncio.run(init_db())
    app.dependency_overrides[get_session] = get_session_override

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    asyncio.run(engine.dispose())
