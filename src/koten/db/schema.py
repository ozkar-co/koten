from __future__ import annotations

import sqlite3


def create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS languages (
            code TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            parser TEXT NOT NULL DEFAULT 'greedy'
        );

        CREATE TABLE IF NOT EXISTS roots (
            lapag_root TEXT PRIMARY KEY,
            meaning TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS root_equivalences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language_code TEXT NOT NULL,
            language_root TEXT NOT NULL,
            lapag_root TEXT NOT NULL,
            UNIQUE(language_code, language_root, lapag_root),
            FOREIGN KEY(language_code) REFERENCES languages(code),
            FOREIGN KEY(lapag_root) REFERENCES roots(lapag_root)
        );

        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            language_code TEXT NOT NULL,
            word TEXT NOT NULL,
            normalized_word TEXT NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(language_code, normalized_word),
            FOREIGN KEY(language_code) REFERENCES languages(code)
        );

        CREATE TABLE IF NOT EXISTS word_root_matches (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL,
            position INTEGER NOT NULL,
            source_root TEXT NOT NULL,
            lapag_root TEXT NOT NULL,
            meaning TEXT,
            UNIQUE(word_id, position, source_root, lapag_root),
            FOREIGN KEY(word_id) REFERENCES words(id) ON DELETE CASCADE,
            FOREIGN KEY(lapag_root) REFERENCES roots(lapag_root)
        );

        CREATE TABLE IF NOT EXISTS word_translations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL,
            target_language_code TEXT NOT NULL,
            translation TEXT NOT NULL,
            source TEXT NOT NULL DEFAULT 'manual',
            UNIQUE(word_id, target_language_code, translation),
            FOREIGN KEY(word_id) REFERENCES words(id) ON DELETE CASCADE,
            FOREIGN KEY(target_language_code) REFERENCES languages(code)
        );

        CREATE INDEX IF NOT EXISTS idx_words_lang_norm
            ON words(language_code, normalized_word);

        CREATE INDEX IF NOT EXISTS idx_equiv_lang_root
            ON root_equivalences(language_code, language_root);

        CREATE INDEX IF NOT EXISTS idx_word_root_word
            ON word_root_matches(word_id);
        """
    )

    connection.commit()
