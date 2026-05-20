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

import re
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


def _replace_koten_word(match: re.Match) -> str:
    prefix = match.group(1)
    word = match.group(2)
    language = LANGUAGE_PREFIXES.get(prefix, DEFAULT_LANGUAGE) if prefix else DEFAULT_LANGUAGE
    image_url = f"/api/word/{language}/{word}"
    return (
        f'<span class="koten-word" data-language="{language}" data-word="{word}">'
        f'<img src="{image_url}" alt="{word}" loading="lazy">'
        f"</span>"
    )


def parse_lore_md(text: str) -> str:
    """
    Convert a lore Markdown string to HTML.

    Koten word references (/word/ or /X/word/) are converted to
    <span class="koten-word"> tags with an embedded image pointing to
    the symbol API. Standard Markdown is then rendered around them.
    """
    # Step 1: protect koten spans from the markdown renderer by converting
    # them first into placeholder tokens, render markdown, then restore.
    # Simpler approach: substitute koten words, then render markdown.
    # Works because our spans are block-safe inside paragraphs.
    substituted = _KOTEN_RE.sub(_replace_koten_word, text)

    # Step 2: render standard Markdown → HTML
    html = markdown.markdown(
        substituted,
        extensions=["tables", "fenced_code"],
    )
    return html


def parse_lore_file(path: str) -> str:
    """Read a lore .md file and return rendered HTML."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    return parse_lore_md(text)
