from fastapi.testclient import TestClient

from koten.lore.md_parser import parse_lore_md
from koten.main import app


def test_parse_lore_md_keeps_quotes_around_koten_words() -> None:
    html = parse_lore_md('tierras malditas "/choseg/". Aun')

    assert '"<span class="koten-word"' in html
    assert '&gt;&lt;img' not in html
    assert 'loading="lazy"&gt;' not in html


def test_parse_lore_md_renders_standalone_image_routes() -> None:
    html = parse_lore_md('/api/image/mapa.jpg')

    assert '<img class="lore-image" src="/api/image/mapa.jpg"' in html


def test_top_level_lore_document_renders() -> None:
    client = TestClient(app)

    response = client.get('/lore/koten')

    assert response.status_code == 200
    assert '/api/image/mapa.jpg' in response.text
    assert '/api/word/lapag/choseg' in response.text