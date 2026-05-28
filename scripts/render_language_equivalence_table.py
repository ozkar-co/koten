#!/usr/bin/env python3
"""Render the language equivalence table in lore/lang/lang.md as a PNG image.

This script reads the markdown table, loads the language symbol configs directly
from src/koten/symbols/configs, and composes the table into a single image that
can be stored under data/images.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageOps

from koten.symbols.config import SymbolConfig


PROJECT_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SOURCE = PROJECT_ROOT / "lore" / "lang" / "lang.md"
DEFAULT_OUTPUT = PROJECT_ROOT / "data" / "images" / "tabla_equivalencias_idiomas.png"
CONFIG_DIR = PROJECT_ROOT / "src" / "koten" / "symbols" / "configs"

LANGUAGE_CONFIGS = {
    "Lapag": "lapag",
    "Gox'jix": "goxjix",
    "Dekayun": "dekayun",
    "Jobid'e": "jobide",
    "Negelsh": "negelsh",
    "Gornash-Kagsha": "gornash_kagsha",
}

CELL_PADDING_X = 16
CELL_PADDING_Y = 14
SYMBOL_MAX_SIZE = 110
HEADER_FONT_SIZE = 22
BODY_FONT_SIZE = 20
LABEL_FONT_SIZE = 16
TITLE_FONT_SIZE = 24

BG_COLOR = "#f7f3ee"
GRID_COLOR = "#b9b1a6"
HEADER_BG = "#24313a"
HEADER_FG = "#ffffff"
ROW_HEADER_BG = "#e7ddd0"
ROW_BG = "#fcfaf7"
TEXT_COLOR = "#1e1e1e"
TITLE_COLOR = "#24313a"


def load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for candidate in candidates:
        path = Path(candidate)
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    return ImageFont.load_default()


def parse_markdown_table(source_path: Path) -> tuple[list[str], list[list[str]]]:
    lines = source_path.read_text(encoding="utf-8").splitlines()

    start_index = None
    for index, line in enumerate(lines):
        if line.startswith("| 0 |"):
            start_index = index
            break

    if start_index is None:
        raise ValueError("Could not find the language equivalence table in the source markdown.")

    table_lines: list[str] = []
    for line in lines[start_index:]:
        if not line.startswith("|"):
            break
        table_lines.append(line)

    if len(table_lines) < 2:
        raise ValueError("The language equivalence table is too short to render.")

    rows: list[list[str]] = []
    for line in table_lines:
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if cells and all(set(cell) <= {"-"} for cell in cells if cell):
            continue
        rows.append(cells)

    if len(rows) < 2:
        raise ValueError("The parsed table does not contain data rows.")

    header = rows[0]
    data_rows = rows[1:]
    return header, data_rows


_TOKEN_RE = re.compile(r"^/(?:([A-Z])/)?(.+?)/$")


def parse_symbol_token(cell: str) -> str:
    match = _TOKEN_RE.match(cell)
    if not match:
        return cell
    return match.group(2)


def measure_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont) -> tuple[int, int]:
    bbox = draw.textbbox((0, 0), text, font=font)
    return bbox[2] - bbox[0], bbox[3] - bbox[1]


def build_image(source_path: Path, output_path: Path) -> Path:
    header_font = load_font(HEADER_FONT_SIZE)
    body_font = load_font(BODY_FONT_SIZE)
    label_font = load_font(LABEL_FONT_SIZE)
    title_font = load_font(TITLE_FONT_SIZE)

    header, data_rows = parse_markdown_table(source_path)
    if not header or header[0] != "0":
        raise ValueError("Unexpected table header; the first column must be the root column '0'.")

    language_headers = header[1:]
    configs: dict[str, SymbolConfig] = {}
    for language_name, language_code in LANGUAGE_CONFIGS.items():
        config_path = CONFIG_DIR / f"{language_code}.json"
        configs[language_name] = SymbolConfig(language_code, config_path)

    symbol_rows: list[list[tuple[Image.Image | str, str]]] = []
    max_symbol_height = 0
    max_label_height = 0

    canvas_probe = Image.new("RGBA", (10, 10), (0, 0, 0, 0))
    probe_draw = ImageDraw.Draw(canvas_probe)

    for row in data_rows:
        if len(row) != len(header):
            raise ValueError(f"Row has {len(row)} cells but expected {len(header)}: {row}")

        row_cells: list[tuple[Image.Image | str, str]] = [(row[0], row[0])]
        for language_name, cell in zip(language_headers, row[1:], strict=True):
            token = parse_symbol_token(cell)
            try:
                symbol = configs[language_name].extract_symbol_for_root(token).convert("RGBA")
                symbol = ImageOps.contain(
                    symbol,
                    (SYMBOL_MAX_SIZE, SYMBOL_MAX_SIZE),
                    Image.Resampling.LANCZOS,
                )
                max_symbol_height = max(max_symbol_height, symbol.height)
                max_label_height = max(max_label_height, measure_text(probe_draw, token, label_font)[1])
                row_cells.append((symbol, token))
            except ValueError:
                max_label_height = max(max_label_height, measure_text(probe_draw, token, label_font)[1])
                row_cells.append((token, token))
        symbol_rows.append(row_cells)

    root_col_width = max(
        measure_text(probe_draw, header[0], header_font)[0],
        max(measure_text(probe_draw, row[0][0], body_font)[0] for row in symbol_rows),
    ) + CELL_PADDING_X * 2

    column_widths: list[int] = [root_col_width]
    for index, language_name in enumerate(language_headers, start=1):
        header_width = measure_text(probe_draw, language_name, header_font)[0]
        cell_width = max(
            header_width,
            max(
                (
                    measure_text(probe_draw, symbol_row[index][0], body_font)[0]
                    if isinstance(symbol_row[index][0], str)
                    else symbol_row[index][0].width
                )
                for symbol_row in symbol_rows
            ),
        ) + CELL_PADDING_X * 2
        column_widths.append(cell_width)

    row_height = max(max_symbol_height + max_label_height + 8, measure_text(probe_draw, "Ag", body_font)[1]) + CELL_PADDING_Y * 2
    header_height = max(measure_text(probe_draw, header[0], header_font)[1], measure_text(probe_draw, "Ag", header_font)[1]) + CELL_PADDING_Y * 2
    title_height = measure_text(probe_draw, "Tabla de equivalencias de idiomas", title_font)[1] + 24

    table_width = sum(column_widths) + 1
    table_height = header_height + row_height * len(symbol_rows) + 1
    canvas = Image.new("RGBA", (table_width + 80, table_height + title_height + 40), BG_COLOR)
    draw = ImageDraw.Draw(canvas)

    x0 = 40
    y0 = 20 + title_height

    title = "Tabla de equivalencias de idiomas"
    title_width, title_text_height = measure_text(draw, title, title_font)
    draw.text(
        (x0 + (table_width - 1 - title_width) / 2, 20),
        title,
        fill=TITLE_COLOR,
        font=title_font,
    )

    def cell_box(col: int, row: int) -> tuple[int, int, int, int]:
        x = x0 + sum(column_widths[:col])
        y = y0 + (header_height if row > 0 else 0) + row_height * max(row - 1, 0)
        if row == 0:
            return x, y0, x + column_widths[col], y0 + header_height
        return x, y, x + column_widths[col], y + row_height

    # Header row
    for col, label in enumerate(header):
        left, top, right, bottom = cell_box(col, 0)
        draw.rectangle([left, top, right, bottom], fill=HEADER_BG, outline=GRID_COLOR, width=2)
        text_w, text_h = measure_text(draw, label, header_font)
        draw.text(
            (left + (right - left - text_w) / 2, top + (bottom - top - text_h) / 2 - 1),
            label,
            fill=HEADER_FG,
            font=header_font,
        )

    # Data rows
    for row_index, row_cells in enumerate(symbol_rows, start=1):
        for col_index, value in enumerate(row_cells):
            left, top, right, bottom = cell_box(col_index, row_index)
            fill = ROW_HEADER_BG if col_index == 0 else ROW_BG
            draw.rectangle([left, top, right, bottom], fill=fill, outline=GRID_COLOR, width=2)

            if col_index == 0:
                text = str(value[0])
                text_w, text_h = measure_text(draw, text, body_font)
                draw.text(
                    (left + (right - left - text_w) / 2, top + (bottom - top - text_h) / 2 - 1),
                    text,
                    fill=TEXT_COLOR,
                    font=body_font,
                )
            else:
                symbol, label = value
                label_w, label_h = measure_text(draw, label, label_font)
                if isinstance(symbol, str):
                    symbol_w, symbol_h = measure_text(draw, symbol, body_font)
                    draw.text(
                        (left + (right - left - symbol_w) / 2, top + 4),
                        symbol,
                        fill=TEXT_COLOR,
                        font=body_font,
                    )
                else:
                    x = left + (right - left - symbol.width) // 2
                    y = top + 4
                    canvas.alpha_composite(symbol, (x, y))
                draw.text(
                    (left + (right - left - label_w) / 2, bottom - CELL_PADDING_Y - label_h),
                    label,
                    fill=TEXT_COLOR,
                    font=label_font,
                )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.convert("RGBA").save(output_path)
    return output_path


def main() -> int:
    parser = argparse.ArgumentParser(description="Render the language equivalence table as a PNG.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE, help="Markdown source file containing the table.")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT, help="Output PNG path.")
    args = parser.parse_args()

    output = build_image(args.source, args.output)
    print(f"Rendered table image: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
