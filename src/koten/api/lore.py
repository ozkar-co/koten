"""Lore document endpoints — return rendered HTML from Markdown lore files."""

from pathlib import Path
import re

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from koten.lore.md_parser import LANGUAGE_PREFIXES, parse_lore_file, parse_lore_md

router = APIRouter(prefix="/lore", tags=["lore"])

# Root directories (resolved at import time)
_LORE_DIR = Path(__file__).parent.parent.parent.parent / "lore"
_SECTION_RE = re.compile(r"^[a-z0-9_-]+$")


def _resolve_section_dir(section: str) -> Path:
    """Resolve and validate a lore section directory."""
    if not _SECTION_RE.match(section):
        raise HTTPException(status_code=400, detail="Invalid section")

    section_dir = (_LORE_DIR / section).resolve()
    if not str(section_dir).startswith(str(_LORE_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not section_dir.exists() or not section_dir.is_dir():
        raise HTTPException(status_code=404, detail=f"Section not found: {section}")
    return section_dir


def _list_sections() -> list[str]:
    """Return all first-level section directory names under lore/."""
    if not _LORE_DIR.exists():
        return []
    sections = [
        item.name
        for item in _LORE_DIR.iterdir()
        if item.is_dir() and not item.name.startswith(".")
    ]
    return sorted(sections)


def _resolve_lore_path(section: str, slug: str) -> Path:
    """Return the path for a lore file, raising 404 if not found."""
    section_dir = _resolve_section_dir(section)
    path = (section_dir / f"{slug}.md").resolve()
    # Guard against path traversal
    if not str(path).startswith(str(_LORE_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"Lore file not found: {section}/{slug}")
    return path


def _resolve_top_level_lore_path(slug: str) -> Path:
    """Return the path for a top-level lore file, raising 404 if not found."""
    path = (_LORE_DIR / f"{slug}.md").resolve()
    if not str(path).startswith(str(_LORE_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid path")
    if not path.exists() or path.parent != _LORE_DIR.resolve():
        raise HTTPException(status_code=404, detail=f"Lore file not found: {slug}")
    return path


def _get_section_index(section: str) -> list[dict]:
    """Return list of documents in a section."""
    section_dir = _resolve_section_dir(section)
    
    docs = []
    for md_file in sorted(section_dir.glob("*.md")):
        if md_file.name == "README.md":
            continue
        slug = md_file.stem
        # Read first line as title (typically the # Heading)
        with open(md_file, "r", encoding="utf-8") as f:
            first_line = f.readline().strip()
            title = first_line.lstrip("# ").strip() if first_line.startswith("#") else slug
        
        docs.append({
            "slug": slug,
            "title": title,
        })
    
    return docs


@router.get("/index")
def get_lore_index() -> dict:
    """Return index of all lore sections and documents."""
    sections_index: dict[str, list[dict]] = {}
    for section in _list_sections():
        sections_index[section] = _get_section_index(section)
    
    return {
        # Backward compatible keys
        "races": sections_index.get("races", []),
        "languages": sections_index.get("lang", []),
        # Dynamic section index
        "sections": sections_index,
        "prefixes": LANGUAGE_PREFIXES,
    }


@router.get("/sections")
def list_sections() -> dict[str, list[str]]:
    """Return all lore section names discovered under lore/."""
    return {"sections": _list_sections()}


@router.get("/races")
def list_races() -> dict:
    """Return list of all races."""
    return {"races": _get_section_index("races")}


@router.get("/lang")
def list_languages() -> dict:
    """Return list of all languages."""
    return {"languages": _get_section_index("lang")}


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


@router.get("/{section}/{slug}", response_class=HTMLResponse)
def get_section_lore(section: str, slug: str) -> HTMLResponse:
    """Return rendered HTML for any lore section document."""
    path = _resolve_lore_path(section, slug)
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


@router.get("/{slug}", response_class=HTMLResponse)
def get_top_level_lore(slug: str) -> HTMLResponse:
    """Return rendered HTML for a top-level lore document."""
    path = _resolve_top_level_lore_path(slug)
    return HTMLResponse(content=parse_lore_file(str(path)))
