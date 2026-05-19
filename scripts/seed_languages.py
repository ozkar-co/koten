from __future__ import annotations

import re
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_PATH = PROJECT_ROOT / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))

from koten.db.connection import get_connection
from koten.db.schema import create_schema
from koten.linguistics.service import canonical_root

LORE_PATH = Path("lore/idiomas.md")

LANGUAGE_LABEL_TO_CODE = {
    "lapag": "lapag",
    "gox'jix": "goxjix",
    "dekayun": "dekayun",
    "jobid'e": "jobide",
    "negelch": "negelch",
    "gornach-kagsha": "gornach_kagsha",
}

LANGUAGE_NAMES = {
    "lapag": "Lapag",
    "goxjix": "Gox'jix",
    "dekayun": "Dekayun",
    "jobide": "Jobid'e",
    "negelch": "Negelch",
    "gornach_kagsha": "Gornach-Kagsha",
}


def _split_row(line: str) -> list[str]:
    raw = [item.strip() for item in re.split(r"\s+", line.strip()) if item.strip()]
    return raw


def parse_translation_rows(text: str) -> tuple[list[str], list[list[str]]]:
    lines = [line for line in text.splitlines() if line.strip()]
    start = next(
        i for i, line in enumerate(lines) if line.lower().startswith("lapag")
    )

    header = _split_row(lines[start])
    rows: list[list[str]] = []

    for line in lines[start + 1 :]:
        if line.startswith("El carácter") or line.startswith("##"):
            break

        parts = _split_row(line)
        if len(parts) == len(header):
            rows.append(parts)

    return header, rows


def parse_semantic_roots(text: str) -> dict[str, str]:
    in_section = False
    roots: dict[str, list[str]] = {}

    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "## Raíces Semánticas":
            in_section = True
            continue

        if in_section and stripped.startswith("Combinando estas raíces"):
            break

        if not in_section or not stripped:
            continue

        match = re.match(r"^([a-z]{1,2}):\s*(.+)$", stripped, flags=re.IGNORECASE)
        if not match:
            continue

        root = canonical_root(match.group(1))
        meaning = match.group(2).strip()
        roots.setdefault(root, []).append(meaning)

    return {key: " | ".join(dict.fromkeys(values)) for key, values in roots.items()}


def seed() -> None:
    text = LORE_PATH.read_text(encoding="utf-8")
    header, translation_rows = parse_translation_rows(text)
    semantic_roots = parse_semantic_roots(text)

    language_codes = [LANGUAGE_LABEL_TO_CODE[label] for label in header]

    with get_connection() as connection:
        connection.execute("PRAGMA foreign_keys = ON;")
        create_schema(connection)

        for code in language_codes:
            connection.execute(
                """
                INSERT INTO languages(code, name, parser)
                VALUES (?, ?, 'greedy')
                ON CONFLICT(code) DO UPDATE SET name = excluded.name
                """,
                (code, LANGUAGE_NAMES.get(code, code.capitalize())),
            )

        for lapag_root, meaning in semantic_roots.items():
            connection.execute(
                """
                INSERT INTO roots(lapag_root, meaning)
                VALUES (?, ?)
                ON CONFLICT(lapag_root) DO UPDATE SET meaning = excluded.meaning
                """,
                (lapag_root, meaning),
            )

        lapag_index = header.index("lapag")

        for row in translation_rows:
            lapag_root = canonical_root(row[lapag_index])
            for idx, language_label in enumerate(header):
                language_code = LANGUAGE_LABEL_TO_CODE[language_label]
                language_root = canonical_root(row[idx])

                connection.execute(
                    """
                    INSERT INTO root_equivalences(language_code, language_root, lapag_root)
                    VALUES (?, ?, ?)
                    ON CONFLICT(language_code, language_root, lapag_root) DO NOTHING
                    """,
                    (language_code, language_root, lapag_root),
                )

        connection.commit()

    print(f"Languages seeded: {len(language_codes)}")
    print(f"Semantic roots seeded: {len(semantic_roots)}")
    print(f"Root equivalences seeded: {len(translation_rows) * len(language_codes)}")


if __name__ == "__main__":
    seed()
