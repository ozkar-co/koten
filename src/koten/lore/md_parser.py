"""
Parser for Koten lore Markdown files.

Koten word syntax within MD text:
  /word/          → implicit Lapag (default)
  /L/word/        → explicit Lapag
  /G/word/        → Gox'jix
  /D/word/        → Dekayun
  /N/word/        → Negelch
  /I/word/        → Idoling
  /J/word/        → Jobid'e
  /K/word/        → Gornach-Kagsha

Output: HTML with <span class="koten-word"> tags that the frontend
can use to request the symbol image from /api/word/{language}/{word}.
"""

from __future__ import annotations

import html
from pathlib import Path
import re
import unicodedata
from urllib.parse import quote

import markdown

# Maps single-letter prefix → language_code
LANGUAGE_PREFIXES: dict[str, str] = {
    "L": "lapag",
    "G": "goxjix",
    "D": "dekayun",
    "N": "negelch",
    "I": "idoling",
    "J": "jobide",
    "K": "gornach_kagsha",
}

DEFAULT_LANGUAGE = "lapag"

# Matches /PREFIX/word/ or /word/
# PREFIX is a single uppercase letter from LANGUAGE_PREFIXES keys
_PREFIX_PATTERN = "|".join(re.escape(k) for k in LANGUAGE_PREFIXES)
_KOTEN_RE = re.compile(
    r"/(?:(" + _PREFIX_PATTERN + r")/)?([^/\s][^/]*)/",
)
_IMAGE_LINE_RE = re.compile(
    r"(?m)^(?P<indent>[ \t]*)(?P<source>(?:/api/image/)?[A-Za-z0-9_.-]+\.(?:png|jpg|jpeg|gif|webp)(?:\?type=(?:full|thumb))?)[ \t]*$"
)
_MARKDOWN_IMAGE_RE = re.compile(
    r"!\[(?P<alt>[^\]]*)\]\((?P<source>[^)\s]+)\)"
)
_PLACEHOLDER_PREFIX = "@@KOTEN_WORD_PLACEHOLDER_"
_PLACEHOLDER_SUFFIX = "@@"


def _strip_accents(text: str) -> str:
    normalized = unicodedata.normalize("NFD", text)
    return "".join(ch for ch in normalized if unicodedata.category(ch) != "Mn")


def _replace_image_line(match: re.Match) -> str:
    source = match.group("source")
    image_url = source if source.startswith("/api/image/") else f"/api/image/{source}"
    image_name = source.split("?", 1)[0].rsplit("/", 1)[-1]
    alt = Path(image_name).stem.replace("_", " ")
    return (
        f'<img class="lore-image" src="{html.escape(image_url, quote=True)}" '
        f'alt="{html.escape(alt, quote=True)}" loading="lazy">'
    )


def _replace_markdown_image(match: re.Match) -> str:
    alt = match.group("alt")
    source = match.group("source")
    image_url = source if source.startswith("/api/image/") else f"/api/image/{source.lstrip('/')}"
    image_name = source.split("?", 1)[0].rsplit("/", 1)[-1]
    fallback_alt = Path(image_name).stem.replace("_", " ")
    final_alt = alt or fallback_alt
    return (
        f'<img class="lore-image" src="{html.escape(image_url, quote=True)}" '
        f'alt="{html.escape(final_alt, quote=True)}" loading="lazy">'
    )


def _replace_koten_word(match: re.Match) -> str:
    prefix = match.group(1)
    word = match.group(2)
    language = LANGUAGE_PREFIXES.get(prefix, DEFAULT_LANGUAGE) if prefix else DEFAULT_LANGUAGE
    normalized_word = _strip_accents(word)
    image_url = f"/api/word/{language}/{quote(normalized_word, safe='')}"
    return (
        f'<span class="koten-word" data-language="{html.escape(language, quote=True)}" '
        f'data-word="{html.escape(normalized_word, quote=True)}">'
        f'<img src="{html.escape(image_url, quote=True)}" alt="{html.escape(normalized_word, quote=True)}" loading="lazy">'
        f"</span>"
    )


def parse_lore_md(text: str) -> str:
    """
    Convert a lore Markdown string to HTML.

    Koten word references (/word/ or /X/word/) are converted to
    <span class="koten-word"> tags with an embedded image pointing to
    the symbol API. Standard Markdown is then rendered around them.
    """
    placeholders: list[str] = []

    def replace_with_placeholder(match: re.Match) -> str:
        placeholders.append(_replace_koten_word(match))
        return f"{_PLACEHOLDER_PREFIX}{len(placeholders) - 1}{_PLACEHOLDER_SUFFIX}"

    def replace_image_with_placeholder(match: re.Match) -> str:
        placeholders.append(_replace_image_line(match))
        return f"{_PLACEHOLDER_PREFIX}{len(placeholders) - 1}{_PLACEHOLDER_SUFFIX}"

    def replace_markdown_image_with_placeholder(match: re.Match) -> str:
        placeholders.append(_replace_markdown_image(match))
        return f"{_PLACEHOLDER_PREFIX}{len(placeholders) - 1}{_PLACEHOLDER_SUFFIX}"

    # Render Markdown around inert placeholders, then restore the generated HTML.
    substituted = _IMAGE_LINE_RE.sub(replace_image_with_placeholder, text)
    substituted = _MARKDOWN_IMAGE_RE.sub(replace_markdown_image_with_placeholder, substituted)
    substituted = _KOTEN_RE.sub(replace_with_placeholder, substituted)

    # Step 2: render standard Markdown → HTML
    html = markdown.markdown(
        substituted,
        extensions=["tables", "fenced_code"],
    )

    for index, replacement in enumerate(placeholders):
        html = html.replace(f"{_PLACEHOLDER_PREFIX}{index}{_PLACEHOLDER_SUFFIX}", replacement)

    return html


def parse_lore_file(path: str) -> str:
    """Read a lore .md file and return rendered HTML."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return parse_lore_md(text)
