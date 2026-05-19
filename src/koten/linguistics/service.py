from __future__ import annotations

import re
import sqlite3
import unicodedata
from dataclasses import dataclass
from typing import Iterable


VOWELS = set("aeiou")


@dataclass
class RootCandidate:
    position: int
    source_root: str
    lapag_roots: list[str]


def canonical_root(root: str) -> str:
    return "".join(sorted(root.strip().lower()))


def normalize_word(word: str) -> str:
    normalized = unicodedata.normalize("NFD", word.lower())
    normalized = "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")
    return re.sub(r"[^a-z]", "", normalized)


def _split_units(word: str, language_code: str) -> list[str]:
    text = normalize_word(word)
    if language_code in {"lapag", "goxjix", "dekayun", "jobide", "negelch", "gornach_kagsha"}:
        return [ch for ch in text if ch not in VOWELS]

    # Fallback for languages with syllabic roots or mixed systems.
    return [ch for ch in text]


def _greedy_extract(units: list[str], known_roots: set[str]) -> list[str]:
    roots: list[str] = []
    i = 0

    while i < len(units):
        if i + 1 < len(units):
            pair = canonical_root(units[i] + units[i + 1])
            if pair in known_roots:
                roots.append(pair)
                i += 2
                continue

        single = canonical_root(units[i])
        roots.append(single)
        i += 1

    return roots


def _known_language_roots(connection: sqlite3.Connection, language_code: str) -> set[str]:
    rows = connection.execute(
        """
        SELECT DISTINCT language_root
        FROM root_equivalences
        WHERE language_code = ?
        """,
        (language_code,),
    ).fetchall()
    return {canonical_root(row["language_root"]) for row in rows}


def _to_lapag_roots(
    connection: sqlite3.Connection, language_code: str, source_roots: Iterable[str]
) -> list[RootCandidate]:
    result: list[RootCandidate] = []

    for position, source_root in enumerate(source_roots):
        mapped = connection.execute(
            """
            SELECT DISTINCT lapag_root
            FROM root_equivalences
            WHERE language_code = ? AND language_root = ?
            ORDER BY lapag_root ASC
            """,
            (language_code, source_root),
        ).fetchall()

        lapag_roots = [row["lapag_root"] for row in mapped]

        # When the word is already in lapag or no mapping exists, keep identity.
        if language_code == "lapag" and not lapag_roots:
            lapag_roots = [source_root]
        elif not lapag_roots:
            lapag_roots = []

        result.append(
            RootCandidate(
                position=position,
                source_root=source_root,
                lapag_roots=lapag_roots,
            )
        )

    return result


def analyze_word(connection: sqlite3.Connection, language_code: str, word: str) -> dict:
    known_roots = _known_language_roots(connection, language_code)
    if language_code == "lapag":
        known_lapag = connection.execute("SELECT lapag_root FROM roots").fetchall()
        known_roots = {row["lapag_root"] for row in known_lapag}

    units = _split_units(word, language_code)
    source_roots = _greedy_extract(units, known_roots) if units else []
    candidates = _to_lapag_roots(connection, language_code, source_roots)

    all_lapag = sorted({lapag for item in candidates for lapag in item.lapag_roots})

    meanings = connection.execute(
        """
        SELECT lapag_root, meaning
        FROM roots
        WHERE lapag_root IN ({placeholders})
        ORDER BY lapag_root ASC
        """.format(placeholders=",".join("?" for _ in all_lapag))
        if all_lapag
        else "SELECT lapag_root, meaning FROM roots WHERE 1=0",
        tuple(all_lapag),
    ).fetchall()

    meaning_map = {row["lapag_root"]: row["meaning"] for row in meanings}

    return {
        "word": word,
        "normalized_word": normalize_word(word),
        "language_code": language_code,
        "roots": [
            {
                "position": item.position,
                "source_root": item.source_root,
                "lapag_roots": item.lapag_roots,
                "meanings": [
                    {"lapag_root": lapag, "meaning": meaning_map.get(lapag)}
                    for lapag in item.lapag_roots
                ],
            }
            for item in candidates
        ],
        "unmapped_roots": [
            item.source_root for item in candidates if not item.lapag_roots
        ],
    }


def upsert_word(
    connection: sqlite3.Connection,
    language_code: str,
    word: str,
    translations: list[dict[str, str]] | None = None,
) -> dict:
    analysis = analyze_word(connection, language_code, word)

    row = connection.execute(
        """
        INSERT INTO words(language_code, word, normalized_word)
        VALUES (?, ?, ?)
        ON CONFLICT(language_code, normalized_word)
        DO UPDATE SET word = excluded.word
        RETURNING id
        """,
        (language_code, word, analysis["normalized_word"]),
    ).fetchone()
    word_id = row["id"]

    connection.execute("DELETE FROM word_root_matches WHERE word_id = ?", (word_id,))

    for root_item in analysis["roots"]:
        for meaning_item in root_item["meanings"]:
            connection.execute(
                """
                INSERT INTO word_root_matches(word_id, position, source_root, lapag_root, meaning)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    word_id,
                    root_item["position"],
                    root_item["source_root"],
                    meaning_item["lapag_root"],
                    meaning_item["meaning"],
                ),
            )

    if translations:
        for item in translations:
            connection.execute(
                """
                INSERT INTO word_translations(word_id, target_language_code, translation, source)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(word_id, target_language_code, translation) DO NOTHING
                """,
                (
                    word_id,
                    item["target_language_code"],
                    item["translation"],
                    item.get("source", "manual"),
                ),
            )

    connection.commit()

    analysis["word_id"] = word_id
    return analysis
