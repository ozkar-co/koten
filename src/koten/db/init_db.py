from pathlib import Path

from sqlalchemy import create_engine, text

from koten.core.config import settings
from koten.db.connection import get_connection
from koten.db.schema import create_schema


LANGUAGE_CODE_RENAMES = {
    "negelch": "negelsh",
    "gornach_kagsha": "gornash_kagsha",
}


def _migrate_language_codes() -> None:
    with get_connection() as sqlite_connection:
        sqlite_connection.execute("PRAGMA foreign_keys = OFF;")

        for old_code, new_code in LANGUAGE_CODE_RENAMES.items():
            row = sqlite_connection.execute(
                "SELECT code, name FROM languages WHERE code = ?",
                (old_code,),
            ).fetchone()
            if not row:
                continue

            sqlite_connection.execute(
                """
                UPDATE root_equivalences
                SET language_code = ?
                WHERE language_code = ?
                """,
                (new_code, old_code),
            )
            sqlite_connection.execute(
                """
                UPDATE words
                SET language_code = ?
                WHERE language_code = ?
                """,
                (new_code, old_code),
            )
            sqlite_connection.execute(
                """
                UPDATE word_translations
                SET target_language_code = ?
                WHERE target_language_code = ?
                """,
                (new_code, old_code),
            )

            sqlite_connection.execute(
                "DELETE FROM languages WHERE code = ?",
                (old_code,),
            )
            sqlite_connection.execute(
                """
                INSERT INTO languages(code, name, parser)
                VALUES (?, ?, 'greedy')
                ON CONFLICT(code) DO UPDATE SET name = excluded.name
                """,
                (new_code, row["name"].replace("Negelch", "Negelsh").replace("Gornach-Kagsha", "Gornash-Kagsha")),
            )

        sqlite_connection.execute("PRAGMA foreign_keys = ON;")
        sqlite_connection.commit()


def initialize_database() -> None:
    db_path = Path(settings.db_file)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    engine = create_engine(f"sqlite:///{db_path}", future=True)
    with engine.begin() as connection:
        connection.execute(text("PRAGMA journal_mode=WAL;"))

    with get_connection() as sqlite_connection:
        sqlite_connection.execute("PRAGMA foreign_keys = ON;")
        create_schema(sqlite_connection)

    _migrate_language_codes()
