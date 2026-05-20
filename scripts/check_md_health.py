#!/usr/bin/env python3
"""Check lore Markdown for broken Koten token markup.

The parser accepts tokens written as /word/ or /X/word/.
This script looks for two common mistakes:

- a missing opening slash before a token, for example ``mash/.``
- an opened token that never closes on the same line

Default scope is ``lore/`` because that is where the Koten token markup is used.
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROOTS = [PROJECT_ROOT / "lore"]
ALLOWED_STANDALONE_PREFIXES = ()
KOTEN_TOKEN_RE = re.compile(
    r"/(?:(?P<prefix>[A-Z])/(?P<prefix_body>[^/\n]+)|(?P<body>[^/\n]+))/"
)


@dataclass(frozen=True)
class Issue:
    path: Path
    line_number: int
    message: str


def iter_markdown_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []

    for root in paths:
        root = root.resolve()

        if root.is_file() and root.suffix.lower() == ".md":
            files.append(root)
            continue

        if root.is_dir():
            files.extend(sorted(root.rglob("*.md")))

    return sorted(dict.fromkeys(files))


def find_issues(path: Path) -> list[Issue]:
    issues: list[Issue] = []
    in_code_block = False

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        stripped = line.strip()

        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue

        if in_code_block:
            continue

        if stripped.startswith(ALLOWED_STANDALONE_PREFIXES):
            continue

        for match in KOTEN_TOKEN_RE.finditer(line):
            body = match.group("prefix_body") or match.group("body") or ""
            if any(character.isspace() for character in body):
                issues.append(
                    Issue(
                        path=path,
                        line_number=line_number,
                        message=(
                            f"token Koten con espacios internos: {match.group(0)}; "
                            "usa el separador correcto del idioma en lugar de espacios"
                        ),
                    )
                )

        for slash_index, character in enumerate(line):
            if character != "/":
                continue

            next_character = line[slash_index + 1 : slash_index + 2]
            if next_character and next_character[0] not in ".,;:!?)}]\"'" and next_character[0] != "":
                continue

            chunk_start = max(line.rfind(" ", 0, slash_index), line.rfind("\t", 0, slash_index)) + 1
            chunk = line[chunk_start:slash_index]
            if not chunk or "/" in line[:slash_index]:
                continue

            issues.append(
                Issue(
                    path=path,
                    line_number=line_number,
                    message=(
                        f"posible falta de '/' antes de '{chunk}/' "
                        f"(se encontró '{chunk}/{next_character or ''}')"
                    ),
                )
            )

        index = 0
        while True:
            slash_index = line.find("/", index)
            if slash_index == -1:
                break

            if line.startswith("//", slash_index):
                index = slash_index + 2
                continue

            if slash_index > 0 and line[slash_index - 1].isalnum():
                index = slash_index + 1
                continue

            closing_index = line.find("/", slash_index + 1)
            if closing_index == -1:
                issues.append(
                    Issue(
                        path=path,
                        line_number=line_number,
                        message="token Koten abierto sin cierre en la misma línea",
                    )
                )
                break

            index = slash_index + 1

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check Markdown lore files for broken Koten token markup."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        type=Path,
        help="Files or directories to inspect. Defaults to lore/.",
    )
    args = parser.parse_args()

    roots = args.paths or DEFAULT_ROOTS
    files = iter_markdown_files(roots)

    if not files:
        print("No se encontraron archivos .md para revisar.")
        return 1

    issues: list[Issue] = []
    for path in files:
        issues.extend(find_issues(path))

    if not issues:
        print(f"OK: {len(files)} archivos Markdown revisados sin problemas.")
        return 0

    print(f"Se encontraron {len(issues)} problemas en {len(files)} archivos Markdown:\n")
    for issue in issues:
        relative_path = issue.path.relative_to(PROJECT_ROOT)
        print(f"{relative_path}:{issue.line_number}: {issue.message}")

    return 1


if __name__ == "__main__":
    raise SystemExit(main())