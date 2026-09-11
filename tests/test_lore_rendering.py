import re

from koten.lore.md_parser import parse_lore_md


def test_parse_lore_md_keeps_quotes_around_koten_words() -> None:
    html = parse_lore_md('tierras malditas "/choseg/". Aun')

    assert '"<span class="koten-word"' in html
    assert "&gt;&lt;img" not in html
    assert 'loading="lazy"&gt;' not in html


def test_parse_lore_md_renders_standalone_image_routes() -> None:
    html = parse_lore_md("mapa.jpg")

    assert '<img class="lore-image" src="/image/mapa.jpg"' in html


def test_parse_lore_md_normalizes_markdown_image_sources() -> None:
    html = parse_lore_md("![Mapa](mapa.jpg)")

    assert '<img class="lore-image" src="/image/mapa.jpg"' in html


def test_parse_lore_md_restores_more_than_ten_placeholders() -> None:
    text = " ".join(["/N/negelch/"] * 12)
    html = parse_lore_md(text)

    assert html.count('<span class="koten-word"') == 12
    assert "@@KPH" not in html


def test_parse_lore_md_does_not_treat_slashes_in_bold_labels_as_koten_words() -> None:
    html = parse_lore_md("**Estrés/Consecuencias**: Pueden ser heridos progresivamente")

    assert "<strong>Estrés/Consecuencias</strong>" in html
    assert 'data-word="Consecuencias**' not in html
    assert "**" not in html


def test_parse_lore_md_does_not_treat_fractions_as_koten_words() -> None:
    html = parse_lore_md("| /gobap/ | Vidrio | Local | 1/3 plástico | 1/12 aluminio |")

    assert html.count('<span class="koten-word"') == 1
    assert 'data-word="gobap"' in html
    assert "1/3" in html
    assert "1/12" in html
    assert "plastico | 1" not in html


def test_parse_lore_md_renders_ordered_list_with_slash_in_bold_label() -> None:
    html = parse_lore_md("5. **Carácter/Mentalidad** - Personalidad")

    assert "<strong>Carácter/Mentalidad</strong>" in html
    assert "<ol" in html
    assert "**" not in html


def test_parse_lore_md_renders_bold_list_items_with_koten_words() -> None:
    html = parse_lore_md(
        "* **Presente:** /N/dus/\n"
        "* **Pasado:** /N/jas/\n"
    )

    assert html.count("<li>") == 2
    assert html.count("<strong>") == 2
    assert html.count('<span class="koten-word"') == 2
    assert "**" not in html


def test_parse_lore_md_nests_items_after_parent_label_with_colon() -> None:
    html = parse_lore_md(
        "* **Marcadores de tiempo:** Detalle:\n"
        "* **Presente:** /N/dus/\n"
        "* **Pasado:** /N/jas/\n"
    )

    assert "<ul>" in html
    assert html.index("Marcadores de tiempo") < html.index("Presente")
    assert re.search(
        r"<li><strong>Marcadores de tiempo:</strong>.*<ul>\s*"
        r"<li><strong>Presente:</strong>",
        html,
        flags=re.DOTALL,
    )


def test_parse_lore_md_renders_bold_link_list_items() -> None:
    html = parse_lore_md("- **[Lapag](lapag.md)**: El lenguaje de la tierra.")

    assert "<strong><a href=\"lapag.md\">Lapag</a></strong>" in html
    assert "**" not in html
