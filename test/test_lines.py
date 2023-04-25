from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_lines_01():
    response = client.get("/lines/92")
    assert response.status_code == 200

    with open("test/lines/92.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_get_conversation_01():
    response = client.get("/lines/conversations/0")
    assert response.status_code == 200

    with open("test/lines/conversation_id=0.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_get_character_lines_01():
    response = client.get("/characters/6957/lines")
    assert response.status_code == 200

    with open("test/lines/character_id=6957.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_404():
    response = client.get("/lines/7414")
    assert response.status_code == 404