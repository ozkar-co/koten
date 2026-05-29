"""API endpoints for symbol-based word image generation."""

from __future__ import annotations

from collections import OrderedDict
from hashlib import sha1
from io import BytesIO
from threading import Lock
import unicodedata
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query, Request
from fastapi.responses import Response, StreamingResponse

from koten.core.config import settings
from koten.symbols import SymbolGenerator

router = APIRouter(tags=["symbols"])
generator = SymbolGenerator()

_CACHE_TTL_SECONDS = 60 * 60 * 24 * 7


class _WordImageCache:
    def __init__(self, max_items: int):
        self._max_items = max(1, max_items)
        self._items: OrderedDict[tuple, bytes] = OrderedDict()
        self._lock = Lock()

    def get(self, key: tuple) -> bytes | None:
        with self._lock:
            value = self._items.get(key)
            if value is None:
                return None
            self._items.move_to_end(key)
            return value

    def put(self, key: tuple, value: bytes) -> None:
        with self._lock:
            self._items[key] = value
            self._items.move_to_end(key)
            while len(self._items) > self._max_items:
                self._items.popitem(last=False)


image_cache = _WordImageCache(settings.word_image_cache_max_items)


def _normalize_render_word(word: str) -> str:
    normalized = unicodedata.normalize("NFD", word)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _cache_key(
    language: str,
    word: str,
    target_height: int | None,
    spacing_x: int | None,
    spacing_y: int | None,
) -> tuple:
    return (
        language,
        word,
        target_height,
        spacing_x,
        spacing_y,
    )


def _response_headers(
    normalized_word: str,
    language: str,
    is_small: bool,
    image_bytes: bytes,
    cache_status: str,
) -> dict[str, str]:
    variant = "small" if is_small else "full"
    etag = sha1(image_bytes).hexdigest()
    return {
        "Content-Disposition": (
            f'inline; filename="{normalized_word}_{language}_{variant}.png"'
        ),
        "Cache-Control": f"public, max-age={_CACHE_TTL_SECONDS}",
        "ETag": f'"{etag}"',
        "X-Word-Cache": cache_status,
    }


@router.get("/word/{language}/{word}")
def generate_word_image(
    request: Request,
    language: str,
    word: str,
    small: bool = Query(
        False,
        description="If true, returns a compact rendering with target height of 24px",
    ),
    spacing_x: int | None = Query(
        None,
        description="Optional horizontal spacing override between rendered symbols",
    ),
    spacing_y: int | None = Query(
        None,
        description="Optional vertical spacing override for vertical/circular layouts",
    ),
) -> StreamingResponse:
    """
    Generate an image of a word in a specified language.

    Args:
        language: Language code (e.g., 'lapag', 'goxjix')
        word: Space-separated roots/syllables to render
        small: If true, render using a compact 24px target height
        spacing_x: Optional horizontal spacing override
        spacing_y: Optional vertical spacing override

    Returns:
        PNG image of the rendered word
    """
    try:
        normalized_word = _normalize_render_word(unquote(word))
        target_height = 24 if small else None
        key = _cache_key(language, normalized_word, target_height, spacing_x, spacing_y)
        image_bytes = image_cache.get(key)
        cache_status = "HIT"

        if image_bytes is None:
            cache_status = "MISS"
            img = generator.generate_word_image(
                normalized_word,
                language,
                target_height=target_height,
                spacing_x=spacing_x,
                spacing_y=spacing_y,
            )

            buffer = BytesIO()
            img.save(buffer, format="PNG")
            image_bytes = buffer.getvalue()
            image_cache.put(key, image_bytes)

        headers = _response_headers(
            normalized_word=normalized_word,
            language=language,
            is_small=small,
            image_bytes=image_bytes,
            cache_status=cache_status,
        )
        if request.headers.get("if-none-match") == headers["ETag"]:
            return Response(status_code=304, headers=headers)

        return StreamingResponse(
            iter([image_bytes]),
            media_type="image/png",
            headers=headers,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.get("/word")
def generate_word_image_query(
    request: Request,
    language: str = Query(..., description="Language code, e.g. lapag"),
    text: str = Query(..., description="Tokenized word/syllables separated by spaces"),
    small: bool = Query(
        False,
        description="If true, returns a compact rendering with target height of 24px",
    ),
    spacing_x: int | None = Query(
        None,
        description="Optional horizontal spacing override between rendered symbols",
    ),
    spacing_y: int | None = Query(
        None,
        description="Optional vertical spacing override for vertical/circular layouts",
    ),
) -> StreamingResponse:
    """Generate a word image using query params to allow spaces in text easily."""
    return generate_word_image(
        request=request,
        language=language,
        word=text,
        small=small,
        spacing_x=spacing_x,
        spacing_y=spacing_y,
    )
