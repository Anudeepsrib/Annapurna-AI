import asyncio
import sqlite3
from datetime import UTC, datetime

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel

from alembic import command
from alembic.config import Config
from app.models.schemas import GenerationMetadata, PlanRequest
from app.prompts.planner_v1 import PROMPT_VERSION, build_planner_prompts
from app.repositories.plan_repository import PlanRepository


def test_planner_prompt_is_versioned_and_contains_household_context():
    request = PlanRequest(
        householdSize="3",
        spiceLevel="mild",
        dietary="vegetarian",
        pantryInventory=[{"name": "rice", "quantity": "2 kg", "category": "grains"}],
    )

    system_prompt, user_prompt = build_planner_prompts(request)

    assert PROMPT_VERSION == "planner_v1"
    assert "untrusted" in system_prompt
    assert "3 people" in user_prompt
    assert "rice (2 kg)" in user_prompt


def test_plan_repository_saves_and_reads_generation_metadata():
    async def scenario():
        engine = create_async_engine(
            "sqlite+aiosqlite:///:memory:",
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        async with engine.begin() as connection:
            await connection.run_sync(SQLModel.metadata.create_all)

        metadata = GenerationMetadata(
            generation_id="test-generation",
            generated_at=datetime.now(UTC),
            provider="ollama",
            model="test-model",
            prompt_version="planner_v1",
            planner_version="weekly_planner_v1",
            validator_version="day_plan_v1",
            source_status="fallback_llm_unavailable",
            fallback_used=True,
        )
        async with async_session() as session:
            repository = PlanRepository(session)
            await repository.save("local-user", {"schema_version": 2, "plan": []}, metadata)
            saved = await repository.get_latest("local-user")

        assert saved is not None
        assert saved.plan_data["schema_version"] == 2
        assert saved.generation_metadata["generation_id"] == "test-generation"
        assert saved.generation_metadata["fallback_used"] is True
        await engine.dispose()

    asyncio.run(scenario())


def test_migration_upgrades_existing_mealplan_table(tmp_path):
    database_path = tmp_path / "legacy.db"
    with sqlite3.connect(database_path) as connection:
        connection.execute(
            "CREATE TABLE mealplan (id INTEGER PRIMARY KEY, user_id VARCHAR NOT NULL, "
            "created_at DATETIME NOT NULL, plan_json VARCHAR NOT NULL)"
        )
        connection.execute("CREATE INDEX ix_mealplan_user_id ON mealplan (user_id)")
        connection.execute(
            "INSERT INTO mealplan (user_id, created_at, plan_json) VALUES (?, ?, ?)",
            ("local-user", "2026-09-19T00:00:00", '{"schema_version": 1, "plan": []}'),
        )

    config = Config("alembic.ini")
    config.set_main_option("sqlalchemy.url", f"sqlite+aiosqlite:///{database_path.as_posix()}")
    command.upgrade(config, "head")

    with sqlite3.connect(database_path) as connection:
        columns = {row[1] for row in connection.execute("PRAGMA table_info(mealplan)")}
        revision = connection.execute("SELECT version_num FROM alembic_version").fetchone()
        saved_payload = connection.execute("SELECT plan_json FROM mealplan").fetchone()
        tables = {row[0] for row in connection.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}

    assert "generation_metadata_json" in columns
    assert revision == ("0003_household_activity",)
    assert saved_payload == ('{"schema_version": 1, "plan": []}',)
    assert {"pantry_item", "pantry_transaction"}.issubset(tables)
    assert {"meal_execution", "meal_feedback", "leftover"}.issubset(tables)
