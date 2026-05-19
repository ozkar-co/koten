from pathlib import Path

from sqlalchemy import create_engine, text

from koten.core.config import settings
from koten.db.connection import get_connection
from koten.db.schema import create_schema


def initialize_database() -> None:
    db_path = Path(settings.db_file)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as connection:
        connection.execute(text("PRAGMA journal_mode=WAL;"))

    with get_connection() as sqlite_connection:
        sqlite_connection.execute("PRAGMA foreign_keys = ON;")
        create_schema(sqlite_connection)
