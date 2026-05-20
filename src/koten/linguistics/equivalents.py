from __future__ import annotations

import re
import sqlite3
import unicodedata
from itertools import product


def _canonical_root(root: str) -> str:
    return "".join(sorted(root.strip().lower()))


def _normalize_language_root(root: str) -> str:
    normalized = unicodedata.normalize("NFD", root.lower())
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z]", "", normalized)


def get_equivalent_roots_for_lapag(
    connection: sqlite3.Connection, lapag_root: str
) -> list[dict[str, str]]:
    canonical_lapag = _canonical_root(lapag_root)

    direct_rows = connection.execute(
        """
        SELECT language_code, language_root
        FROM root_equivalences
        WHERE lapag_root = ?
        ORDER BY language_code ASC, language_root ASC
        """,
        (canonical_lapag,),
    ).fetchall()

    by_language: dict[str, set[str]] = {}
    for row in direct_rows:
        by_language.setdefault(row["language_code"], set()).add(
            _normalize_language_root(row["language_root"])
        )

    if len(canonical_lapag) > 1:
        languages = connection.execute("SELECT code FROM languages").fetchall()
        for lang_row in languages:
            language_code = lang_row["code"]
            options_per_char: list[list[str]] = []

            for char_root in canonical_lapag:
                char_rows = connection.execute(
                    """
                    SELECT DISTINCT language_root
                    FROM root_equivalences
                    WHERE language_code = ? AND lapag_root = ?
                    ORDER BY language_root ASC
                    """,
                    (language_code, char_root),
                ).fetchall()

                char_options = [
                    _normalize_language_root(row["language_root"]) for row in char_rows
                ]
                if not char_options:
                    options_per_char = []
                    break
                options_per_char.append(char_options)

            if not options_per_char:
                continue

            for parts in product(*options_per_char):
                by_language.setdefault(language_code, set()).add("".join(parts))

    return [
        {
            "language_code": language_code,
            "language_root": language_root,
        }
        for language_code in sorted(by_language)
        for language_root in sorted(by_language[language_code])
    ]
