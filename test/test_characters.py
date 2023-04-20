from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_character_01():
    response = client.get("/characters/7421")
    assert response.status_code == 200

    with open("test/characters/7421.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_get_character_02():
    response = client.get("/characters/6967")
    assert response.status_code == 200

    with open("test/characters/6967.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_get_character_03():
    response = client.get("/characters/bulin")
    assert response.status_code == 422

    with open("test/characters/bulin.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_characters_01():
    response = client.get("/characters/")
    assert response.status_code == 200

    with open("test/characters/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)

# New test case (includes multiple conversation partners)
def test_get_character2():
    response = client.get("/characters/2")
    assert response.status_code == 200

    with open("test/characters/2.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_characters_02():
    response = client.get("/characters/?name=an&offset=5")
    assert response.status_code == 200

    with open("test/characters/characters-name=an&limit=50&offset=5&sort=number_of_lines.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_characters_03():
    response = client.get("/characters/?name=an&offset=-1")
    assert response.status_code == 422


def test_characters_04():
    response = client.get("/characters/?name=an&limit=-1")
    assert response.status_code == 422


def test_sort_filter_01():
    response = client.get(
        "/characters/?name=amy&limit=50&offset=0&sort=number_of_lines"
    )
    assert response.status_code == 200

    with open(
        "test/characters/characters-name=amy&limit=50&offset=0&sort=number_of_lines.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)

# New test case ()
def test_sort_filter2():
    response = client.get(
        "/characters/?name=%20&limit=250&offset=42&sort=movie"
    )
    assert response.status_code == 200

    with open(
        "test/characters/characters-name=space&limit=250&offset=42&sort=movie.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)


def test_sort_filter_02():
    response = client.get(
        "/characters/?name=an&limit=20&offset=10&sort=movie"
    )
    assert response.status_code == 200

    with open(
        "test/characters/characters-name=an&limit=20&offset=10&sort=movie.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)


def test_404():
    response = client.get("/characters/400")
    assert response.status_code == 404
