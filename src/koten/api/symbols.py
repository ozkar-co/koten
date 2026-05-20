"""API endpoints for symbol-based word image generation."""

from __future__ import annotations

from io import BytesIO
from urllib.parse import unquote

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from koten.symbols import SymbolGenerator

router = APIRouter(tags=["symbols"])
generator = SymbolGenerator()


@router.get("/word/{language}/{word}")
def generate_word_image(
    language: str,
    word: str,
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
        spacing_x: Optional horizontal spacing override
        spacing_y: Optional vertical spacing override

    Returns:
        PNG image of the rendered word
    """
    try:
        normalized_word = unquote(word)
        img = generator.generate_word_image(
            normalized_word,
            language,
            spacing_x=spacing_x,
            spacing_y=spacing_y,
        )

        # Convert to PNG bytes
        img_bytes = BytesIO()
        img.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        return StreamingResponse(
            iter([img_bytes.getvalue()]),
            media_type="image/png",
            headers={
                "Content-Disposition": f'inline; filename="{normalized_word}_{language}.png"'
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image generation failed: {str(e)}")


@router.get("/word")
def generate_word_image_query(
    language: str = Query(..., description="Language code, e.g. lapag"),
    text: str = Query(..., description="Tokenized word/syllables separated by spaces"),
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
        language=language,
        word=text,
        spacing_x=spacing_x,
        spacing_y=spacing_y,
    )
