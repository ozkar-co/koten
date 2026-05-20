import sqlite3

from koten.db.schema import create_schema
from koten.linguistics.service import analyze_word, get_equivalent_roots_for_lapag


def _conn() -> sqlite3.Connection:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row
    create_schema(connection)
    return connection


def test_composes_two_char_equivalents_from_single_char_mappings() -> None:
    connection = _conn()

    connection.execute("INSERT INTO languages(code, name, parser) VALUES (?, ?, 'greedy')", ("lapag", "Lapag"))
    connection.execute("INSERT INTO languages(code, name, parser) VALUES (?, ?, 'greedy')", ("foo", "Foo"))

    connection.execute("INSERT INTO roots(lapag_root, meaning) VALUES (?, ?)", ("ab", "dummy"))

    connection.execute(
        "INSERT INTO root_equivalences(language_code, language_root, lapag_root) VALUES (?, ?, ?)",
        ("foo", "x", "a"),
    )
    connection.execute(
        "INSERT INTO root_equivalences(language_code, language_root, lapag_root) VALUES (?, ?, ?)",
        ("foo", "y", "b"),
    )
    connection.commit()

    equivalents = get_equivalent_roots_for_lapag(connection, "ab")

    assert {item["language_code"] for item in equivalents} == {"foo"}
    assert {item["language_root"] for item in equivalents} == {"xy"}


def test_keeps_direct_single_char_equivalents() -> None:
    connection = _conn()

    connection.execute("INSERT INTO languages(code, name, parser) VALUES (?, ?, 'greedy')", ("lapag", "Lapag"))
    connection.execute("INSERT INTO languages(code, name, parser) VALUES (?, ?, 'greedy')", ("foo", "Foo"))

    connection.execute("INSERT INTO roots(lapag_root, meaning) VALUES (?, ?)", ("a", "dummy"))
    connection.execute(
        "INSERT INTO root_equivalences(language_code, language_root, lapag_root) VALUES (?, ?, ?)",
        ("foo", "x", "a"),
    )
    connection.commit()

    equivalents = get_equivalent_roots_for_lapag(connection, "a")

    assert equivalents == [{"language_code": "foo", "language_root": "x"}]


def test_gornach_equivalent_keeps_surface_syllable() -> None:
    connection = _conn()

    connection.execute("INSERT INTO languages(code, name, parser) VALUES (?, ?, 'greedy')", ("lapag", "Lapag"))
    connection.execute(
        "INSERT INTO languages(code, name, parser) VALUES (?, ?, 'greedy')",
        ("gornach_kagsha", "Gornach-Kagsha"),
    )

    connection.execute("INSERT INTO roots(lapag_root, meaning) VALUES (?, ?)", ("k", "dummy"))
    connection.execute(
        "INSERT INTO root_equivalences(language_code, language_root, lapag_root) VALUES (?, ?, ?)",
        ("gornach_kagsha", "gar", "k"),
    )
    connection.commit()

    equivalents = get_equivalent_roots_for_lapag(connection, "k")

    assert {item["language_root"] for item in equivalents} == {"gar"}


def test_analyze_word_gornach_matches_syllable_root() -> None:
    connection = _conn()

    connection.execute("INSERT INTO languages(code, name, parser) VALUES (?, ?, 'greedy')", ("lapag", "Lapag"))
    connection.execute(
        "INSERT INTO languages(code, name, parser) VALUES (?, ?, 'greedy')",
        ("gornach_kagsha", "Gornach-Kagsha"),
    )

    connection.execute("INSERT INTO roots(lapag_root, meaning) VALUES (?, ?)", ("k", "dummy"))
    connection.execute(
        "INSERT INTO root_equivalences(language_code, language_root, lapag_root) VALUES (?, ?, ?)",
        ("gornach_kagsha", "gar", "k"),
    )
    connection.commit()

    analysis = analyze_word(connection, "gornach_kagsha", "gar")

    assert analysis["roots"]
    assert analysis["roots"][0]["source_root"] == "gar"
    assert analysis["roots"][0]["lapag_roots"] == ["k"]


def test_gornach_two_char_lapag_root_composes_ordered_syllables() -> None:
    connection = _conn()

    connection.execute("INSERT INTO languages(code, name, parser) VALUES (?, ?, 'greedy')", ("lapag", "Lapag"))
    connection.execute(
        "INSERT INTO languages(code, name, parser) VALUES (?, ?, 'greedy')",
        ("gornach_kagsha", "Gornach-Kagsha"),
    )

    connection.execute("INSERT INTO roots(lapag_root, meaning) VALUES (?, ?)", ("km", "dummy"))
    connection.execute(
        "INSERT INTO root_equivalences(language_code, language_root, lapag_root) VALUES (?, ?, ?)",
        ("gornach_kagsha", "gar", "k"),
    )
    connection.execute(
        "INSERT INTO root_equivalences(language_code, language_root, lapag_root) VALUES (?, ?, ?)",
        ("gornach_kagsha", "nash", "m"),
    )
    connection.commit()

    equivalents = get_equivalent_roots_for_lapag(connection, "km")

    assert {item["language_root"] for item in equivalents} == {"garnash"}
