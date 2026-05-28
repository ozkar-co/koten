from pathlib import Path

from sqlalchemy import create_engine, text

from koten.core.config import settings
from koten.db.connection import get_connection
from koten.db.schema import create_schema
from koten.linguistics.service import canonical_root


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


def _merge_meanings(existing: str, incoming: str) -> str:
    existing_parts = [part.strip() for part in existing.split("|") if part.strip()]
    incoming_parts = [part.strip() for part in incoming.split("|") if part.strip()]
    merged: list[str] = []
    for part in [*existing_parts, *incoming_parts]:
        if part not in merged:
            merged.append(part)
    return " | ".join(merged)


def _migrate_c_alias_to_sh() -> None:
    """Normalize legacy c-based Lapag roots into canonical sh-based roots."""
    with get_connection() as sqlite_connection:
        sqlite_connection.execute("PRAGMA foreign_keys = OFF;")

        root_rows = sqlite_connection.execute(
            "SELECT lapag_root, meaning FROM roots ORDER BY lapag_root ASC"
        ).fetchall()

        mappings: list[tuple[str, str]] = []
        for row in root_rows:
            old_root = row["lapag_root"]
            new_root = canonical_root(old_root)
            if new_root != old_root:
                mappings.append((old_root, new_root))

        for old_root, new_root in mappings:
            old_row = sqlite_connection.execute(
                "SELECT meaning FROM roots WHERE lapag_root = ?",
                (old_root,),
            ).fetchone()
            if not old_row:
                continue

            new_row = sqlite_connection.execute(
                "SELECT meaning FROM roots WHERE lapag_root = ?",
                (new_root,),
            ).fetchone()

            if new_row:
                merged_meaning = _merge_meanings(new_row["meaning"], old_row["meaning"])
                sqlite_connection.execute(
                    "UPDATE roots SET meaning = ? WHERE lapag_root = ?",
                    (merged_meaning, new_root),
                )
            else:
                sqlite_connection.execute(
                    "UPDATE roots SET lapag_root = ? WHERE lapag_root = ?",
                    (new_root, old_root),
                )

            sqlite_connection.execute(
                "UPDATE root_equivalences SET lapag_root = ? WHERE lapag_root = ?",
                (new_root, old_root),
            )
            sqlite_connection.execute(
                "UPDATE word_root_matches SET lapag_root = ? WHERE lapag_root = ?",
                (new_root, old_root),
            )
            sqlite_connection.execute(
                "UPDATE root_equivalences SET language_root = ? WHERE language_code = 'lapag' AND language_root = ?",
                (new_root, old_root),
            )

            sqlite_connection.execute(
                "DELETE FROM roots WHERE lapag_root = ?",
                (old_root,),
            )

        # Normalize language-side legacy roots that used 'c' for the sh sound.
        for code in ("lapag", "goxjix", "dekayun", "negelsh"):
            sqlite_connection.execute(
                "UPDATE root_equivalences SET language_root = 'sh' WHERE language_code = ? AND language_root = 'c'",
                (code,),
            )

        # Remove duplicates that may appear after normalization.
        sqlite_connection.execute(
            """
            DELETE FROM root_equivalences
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM root_equivalences
                GROUP BY language_code, language_root, lapag_root
            )
            """
        )
        sqlite_connection.execute(
            """
            DELETE FROM word_root_matches
            WHERE id NOT IN (
                SELECT MIN(id)
                FROM word_root_matches
                GROUP BY word_id, position, source_root, lapag_root
            )
            """
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
    _migrate_c_alias_to_sh()
