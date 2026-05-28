from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from PIL import Image


def _nt(token: str) -> str:
    if token == " ":
        return " "
    return token.strip().lower()


class SymbolConfig:
    """Configuration for a language's symbol sheet and layout."""

    def __init__(self, language_code: str, config_path: Path):
        self.language_code = language_code
        with open(config_path, "r", encoding="utf-8") as f:
            self.config = json.load(f)

        self.sheet_path = config_path.parent.parent / "sheets" / self.config["sheet_file"]
        if not self.sheet_path.exists():
            raise FileNotFoundError(f"Symbol sheet not found: {self.sheet_path}")

        self.sheet = Image.open(self.sheet_path)
        self.symbol_size = self.config.get("symbol_size", 160)
        self.cols = self.config.get("cols", 10)
        self.rows = self.config.get("rows", 3)

    def _trim_for_root(self, root: str) -> tuple[int, int, int, int]:
        trim_cfg = self.config.get("trim", {})
        per_root = trim_cfg.get("per_root", {})
        root_trim = per_root.get(_nt(root), {})

        left = int(root_trim.get("left", trim_cfg.get("left", 0)))
        right = int(root_trim.get("right", trim_cfg.get("right", 0)))
        top = int(root_trim.get("top", trim_cfg.get("top", 0)))
        bottom = int(root_trim.get("bottom", trim_cfg.get("bottom", 0)))
        return left, right, top, bottom

    def get_symbol_position(self, root: str) -> Optional[tuple[int, int]]:
        mapping = self.config.get("root_mapping", {})
        return mapping.get(_nt(root))

    def extract_symbol(self, row: int, col: int) -> Image.Image:
        x = col * self.symbol_size
        y = row * self.symbol_size
        box = (x, y, x + self.symbol_size, y + self.symbol_size)
        return self.sheet.crop(box)

    def extract_symbol_for_root(self, root: str) -> Image.Image:
        pos = self.get_symbol_position(root)
        if pos is None:
            raise ValueError(f"Root '{root}' not found in {self.language_code}")

        row, col = pos
        symbol = self.extract_symbol(row, col).convert("RGBA")

        left, right, top, bottom = self._trim_for_root(root)
        width, height = symbol.size
        x0 = max(0, min(width - 1, left))
        y0 = max(0, min(height - 1, top))
        x1 = max(x0 + 1, width - max(0, right))
        y1 = max(y0 + 1, height - max(0, bottom))
        return symbol.crop((x0, y0, x1, y1))
