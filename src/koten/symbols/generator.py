"""Generate word images from linguistic symbols."""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PIL import Image

from koten.symbols.config import SymbolConfig
from koten.symbols.tokenizers import get_tokenizer


def _nt(token: str) -> str:
    """Normalize a token for symbol lookup: strip and lowercase, no sorting."""
    return token.strip().lower()


class SymbolGenerator:
    """Generate images of words using linguistic symbols."""

    def __init__(self, symbols_dir: str = "src/koten/symbols"):
        self.symbols_dir = Path(symbols_dir)
        self.configs: dict[str, SymbolConfig] = {}
        self._load_configs()

    def _load_configs(self) -> None:
        """Load all language configurations."""
        configs_dir = self.symbols_dir / "configs"
        if not configs_dir.exists():
            return

        for config_file in configs_dir.glob("*.json"):
            language_code = config_file.stem
            try:
                self.configs[language_code] = SymbolConfig(language_code, config_file)
            except Exception as e:
                print(f"Error loading config for {language_code}: {e}")

    @staticmethod
    def _merge_on_previous(
        base: Image.Image,
        overlay: Image.Image,
        offset_x: int,
        offset_y: int,
    ) -> Image.Image:
        """Merge an overlay glyph on top of a base glyph using alpha compositing."""
        min_x = min(0, offset_x)
        min_y = min(0, offset_y)
        max_x = max(base.width, offset_x + overlay.width)
        max_y = max(base.height, offset_y + overlay.height)

        canvas = Image.new("RGBA", (max_x - min_x, max_y - min_y), (0, 0, 0, 0))
        canvas.alpha_composite(base, (0 - min_x, 0 - min_y))
        canvas.alpha_composite(overlay, (offset_x - min_x, offset_y - min_y))
        return canvas

    def _tokenize(self, word: str, config: SymbolConfig) -> list[str]:
        """Tokenize word using language-specific tokenizer."""
        tokenizer = get_tokenizer(config.language_code)
        root_mapping = config.config.get("root_mapping", {})
        tokens = tokenizer(word, root_mapping)
        return [t for t in tokens if t == " " or t.strip()]

    def _compose_symbols(
        self,
        roots: list[str],
        config: SymbolConfig,
    ) -> list[Image.Image]:
        overlay_cfg = config.config.get("overlay", {})
        overlay_enabled = bool(overlay_cfg.get("enabled", False))
        overlay_roots = {_nt(x) for x in overlay_cfg.get("roots", [])}
        overlay_blockers = {_nt(x) for x in overlay_cfg.get("blockers", [])}
        offset_x = int(overlay_cfg.get("offset_x", 0))
        offset_y = int(overlay_cfg.get("offset_y", 0))

        symbols: list[Image.Image] = []
        previous_roots: list[str] = []
        previous_had_overlay: list[bool] = []

        for root in roots:
            norm = _nt(root)
            symbol = config.extract_symbol_for_root(norm)
            can_overlay = (
                overlay_enabled
                and norm in overlay_roots
                and symbols
                and not previous_had_overlay[-1]
                and previous_roots[-1] not in overlay_blockers
            )

            if can_overlay:
                symbols[-1] = self._merge_on_previous(
                    base=symbols[-1],
                    overlay=symbol,
                    offset_x=offset_x,
                    offset_y=offset_y,
                )
                previous_roots[-1] = f"{previous_roots[-1]}+{norm}"
                previous_had_overlay[-1] = True
                continue

            symbols.append(symbol)
            previous_roots.append(norm)
            previous_had_overlay.append(False)

        return symbols

    @staticmethod
    def _render_horizontal(symbols: list[Image.Image], spacing_x: int) -> Image.Image:
        heights = [symbol.height for symbol in symbols]
        widths = [symbol.width for symbol in symbols]
        total_width = sum(widths) + spacing_x * (len(symbols) - 1)
        total_height = max(heights)

        combined = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))
        x_offset = 0
        for symbol in symbols:
            y_offset = (total_height - symbol.height) // 2
            combined.alpha_composite(symbol, (x_offset, y_offset))
            x_offset += symbol.width + spacing_x
        return combined

    @staticmethod
    def _render_columnar(
        roots: list[str],
        config: SymbolConfig,
        spacing_x: int,
        spacing_y: int,
    ) -> Image.Image:
        column_cfg = config.config.get("columnar", {})
        break_token = _nt(column_cfg.get("break_token", "-"))
        draw_break_in_previous = bool(
            column_cfg.get("draw_break_symbol_in_previous_column", True)
        )

        columns: list[list[str]] = [[]]
        for token in roots:
            token_canonical = _nt(token)
            if token_canonical == break_token:
                if draw_break_in_previous:
                    columns[-1].append(token_canonical)
                columns.append([])
                continue
            columns[-1].append(token_canonical)

        columns = [col for col in columns if col]
        if not columns:
            raise ValueError("No valid roots in word")

        rendered_columns: list[Image.Image] = []
        for column in columns:
            glyphs = [config.extract_symbol_for_root(token) for token in column]
            column_height = sum(g.height for g in glyphs) + spacing_y * (len(glyphs) - 1)
            column_width = max(g.width for g in glyphs)
            column_image = Image.new("RGBA", (column_width, column_height), (0, 0, 0, 0))

            y_offset = 0
            for glyph in glyphs:
                x_offset = (column_width - glyph.width) // 2
                column_image.alpha_composite(glyph, (x_offset, y_offset))
                y_offset += glyph.height + spacing_y
            rendered_columns.append(column_image)

        total_width = sum(col.width for col in rendered_columns) + spacing_x * (
            len(rendered_columns) - 1
        )
        total_height = max(col.height for col in rendered_columns)
        canvas = Image.new("RGBA", (total_width, total_height), (0, 0, 0, 0))

        x_offset = 0
        for col in rendered_columns:
            y_offset = (total_height - col.height) // 2
            canvas.alpha_composite(col, (x_offset, y_offset))
            x_offset += col.width + spacing_x
        return canvas

    @staticmethod
    def _render_circular_clockwise_4(
        symbols: list[Image.Image],
        spacing_x: int,
        spacing_y: int,
    ) -> Image.Image:
        if len(symbols) != 4:
            raise ValueError("This language requires exactly 4 syllables")

        rotated = [
            symbols[0],
            symbols[1].rotate(-90, expand=True),
            symbols[2].rotate(-180, expand=True),
            symbols[3].rotate(-270, expand=True),
        ]

        top_height = max(rotated[0].height, rotated[1].height)
        bottom_height = max(rotated[3].height, rotated[2].height)
        left_width = max(rotated[0].width, rotated[3].width)
        right_width = max(rotated[1].width, rotated[2].width)

        width = left_width + spacing_x + right_width
        height = top_height + spacing_y + bottom_height
        canvas = Image.new("RGBA", (width, height), (0, 0, 0, 0))

        canvas.alpha_composite(
            rotated[0],
            (left_width - rotated[0].width, top_height - rotated[0].height),
        )
        canvas.alpha_composite(
            rotated[1],
            (left_width + spacing_x, top_height - rotated[1].height),
        )
        canvas.alpha_composite(rotated[2], (left_width + spacing_x, top_height + spacing_y))
        canvas.alpha_composite(
            rotated[3],
            (left_width - rotated[3].width, top_height + spacing_y),
        )

        return canvas

    def generate_word_image(
        self,
        word: str,
        language_code: str,
        spacing_x: Optional[int] = None,
        spacing_y: Optional[int] = None,
    ) -> Image.Image:
        if language_code not in self.configs:
            raise ValueError(f"Language not supported: {language_code}")

        config = self.configs[language_code]
        spacing_cfg = config.config.get("spacing", {})
        default_spacing_x = int(spacing_cfg.get("x", config.config.get("padding", 10)))
        default_spacing_y = int(spacing_cfg.get("y", 10))
        spacing_x = default_spacing_x if spacing_x is None else spacing_x
        spacing_y = default_spacing_y if spacing_y is None else spacing_y
        writing_mode = config.config.get("writing_mode", "horizontal")

        roots = self._tokenize(word, config)
        if not roots:
            raise ValueError("No valid roots in word")

        if writing_mode == "columnar_right":
            return self._render_columnar(
                roots=roots,
                config=config,
                spacing_x=spacing_x,
                spacing_y=spacing_y,
            )

        symbols = self._compose_symbols(roots, config)
        if not symbols:
            raise ValueError("No valid roots in word")

        if writing_mode == "circular_clockwise_4":
            return self._render_circular_clockwise_4(
                symbols=symbols,
                spacing_x=spacing_x,
                spacing_y=spacing_y,
            )

        return self._render_horizontal(symbols=symbols, spacing_x=spacing_x)
