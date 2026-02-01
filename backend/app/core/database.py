from sqlmodel import SQLModel, create_engine, Session
from typing import Generator
import os

# Use SQLite for MVP/Free-Tier (File based)
# In production, this env var would be a Postgres URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./annapurna.db")

# check_same_thread=False is needed only for SQLite
connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

def create_db_and_tables():
    """
    Create tables if they don't exist.
    """
    SQLModel.metadata.create_all(engine)

def get_session() -> Generator[Session, None, None]:
    """
    Dependency to provide a DB session per request.
    """
    with Session(engine) as session:
        yield session
