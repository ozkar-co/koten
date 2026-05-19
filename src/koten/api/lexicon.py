from __future__ import annotations

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from koten.db.connection import get_connection
from koten.linguistics.service import analyze_word, canonical_root, upsert_word

router = APIRouter(prefix="/lexicon", tags=["lexicon"])


class AnalyzeRequest(BaseModel):
    language_code: str = Field(min_length=2)
    word: str = Field(min_length=1)


class TranslationInput(BaseModel):
    target_language_code: str = Field(min_length=2)
    translation: str = Field(min_length=1)
    source: str = "manual"


class SaveWordRequest(BaseModel):
    language_code: str = Field(min_length=2)
    word: str = Field(min_length=1)
    translations: list[TranslationInput] = Field(default_factory=list)


@router.post("/analyze")
def analyze(payload: AnalyzeRequest) -> dict:
    with get_connection() as connection:
        exists = connection.execute(
            "SELECT 1 FROM languages WHERE code = ?",
            (payload.language_code,),
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Unknown language")

        return analyze_word(connection, payload.language_code, payload.word)


@router.post("/words")
def save_word(payload: SaveWordRequest) -> dict:
    with get_connection() as connection:
        exists = connection.execute(
            "SELECT 1 FROM languages WHERE code = ?",
            (payload.language_code,),
        ).fetchone()
        if not exists:
            raise HTTPException(status_code=404, detail="Unknown language")

        for item in payload.translations:
            target_exists = connection.execute(
                "SELECT 1 FROM languages WHERE code = ?",
                (item.target_language_code,),
            ).fetchone()
            if not target_exists:
                raise HTTPException(
                    status_code=404,
                    detail=f"Unknown target language: {item.target_language_code}",
                )

        return upsert_word(
            connection,
            payload.language_code,
            payload.word,
            [item.model_dump() for item in payload.translations],
        )


@router.get("/roots/{root}")
def get_root(root: str) -> dict:
    lapag_root = canonical_root(root)

    with get_connection() as connection:
        root_row = connection.execute(
            "SELECT lapag_root, meaning FROM roots WHERE lapag_root = ?",
            (lapag_root,),
        ).fetchone()
        if not root_row:
            raise HTTPException(status_code=404, detail="Root not found")

        equivalents = connection.execute(
            """
            SELECT language_code, language_root
            FROM root_equivalences
            WHERE lapag_root = ?
            ORDER BY language_code ASC, language_root ASC
            """,
            (lapag_root,),
        ).fetchall()

    return {
        "lapag_root": root_row["lapag_root"],
        "meaning": root_row["meaning"],
        "equivalents": [
            {
                "language_code": row["language_code"],
                "language_root": row["language_root"],
            }
            for row in equivalents
        ],
    }


@router.get("/words/search")
def search_words(
    language_code: str = Query(min_length=2),
    q: str = Query(min_length=1),
    limit: int = Query(default=20, ge=1, le=100),
) -> dict:
    with get_connection() as connection:
        rows = connection.execute(
            """
            SELECT id, language_code, word, normalized_word, created_at
            FROM words
            WHERE language_code = ?
              AND normalized_word LIKE '%' || ? || '%'
            ORDER BY id DESC
            LIMIT ?
            """,
            (language_code, q.lower(), limit),
        ).fetchall()

    return {
        "results": [
            {
                "id": row["id"],
                "language_code": row["language_code"],
                "word": row["word"],
                "normalized_word": row["normalized_word"],
                "created_at": row["created_at"],
            }
            for row in rows
        ]
    }
