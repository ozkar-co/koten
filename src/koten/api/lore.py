"""Lore document endpoints — return rendered HTML from Markdown lore files."""

from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from koten.lore.md_parser import LANGUAGE_PREFIXES, parse_lore_file, parse_lore_md

router = APIRouter(prefix="/lore", tags=["lore"])

# Root of the lore directory (relative to project root, resolved at import time)
_LORE_DIR = Path(__file__).parent.parent.parent.parent / "lore"


def _resolve_lore_path(section: str, slug: str) -> Path:
    """Return the path for a lore file, raising 404 if not found."""
    path = (_LORE_DIR / section / f"{slug}.md").resolve()
    # Guard against path traversal
    if not str(path).startswith(str(_LORE_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Lore file not found: {section}/{slug}")
    return path


@router.get("/races/{slug}", response_class=HTMLResponse)
def get_race_lore(slug: str) -> HTMLResponse:
    """Return rendered HTML for a race lore document."""
    path = _resolve_lore_path("races", slug)
    return HTMLResponse(content=parse_lore_file(str(path)))


@router.get("/lang/{slug}", response_class=HTMLResponse)
def get_language_lore(slug: str) -> HTMLResponse:
    """Return rendered HTML for a language lore document."""
    path = _resolve_lore_path("lang", slug)
    return HTMLResponse(content=parse_lore_file(str(path)))


@router.get("/prefixes")
def get_language_prefixes() -> dict[str, str]:
    """Return the mapping of single-letter prefixes to language codes."""
    return LANGUAGE_PREFIXES


@router.post("/render", response_class=HTMLResponse)
def render_markdown(body: dict) -> HTMLResponse:
    """
    Render arbitrary Markdown text with Koten word syntax.
    Body: {"text": "...markdown..."}
    """
    text = body.get("text", "")
    return HTMLResponse(content=parse_lore_md(text))
