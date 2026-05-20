from fastapi.testclient import TestClient

from koten.main import app


def test_health() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_languages_contract() -> None:
    client = TestClient(app)
    response = client.get("/lexicon/languages")

    assert response.status_code == 200
    payload = response.json()
    assert "languages" in payload
    assert isinstance(payload["languages"], list)

    if payload["languages"]:
        first = payload["languages"][0]
        assert "name" in first
        assert "prefix" in first
        assert "code" in first
