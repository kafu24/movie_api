from fastapi.testclient import TestClient

from src.api.server import app

import json

client = TestClient(app)


def test_get_movie_01():
    response = client.get("/movies/44")
    assert response.status_code == 200

    with open("test/movies/44.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_get_movie_02():
    response = client.get("/movies/3")
    assert response.status_code == 200

    with open("test/movies/3.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_movies_01():
    response = client.get("/movies/")
    assert response.status_code == 200

    with open("test/movies/root.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_movies_02():
    response = client.get("/movies/?name=as&limit=20&offset=10&sort=movie_title")
    assert response.status_code == 200

    with open("test/movies/movies-name=as&limit=20&offset=10&sort=movie_title.json", encoding="utf-8") as f:
        assert response.json() == json.load(f)


def test_sort_filter_02():
    response = client.get("/movies/?name=the&limit=50&offset=0&sort=year")
    assert response.status_code == 200

    with open(
        "test/movies/movies-name=the&limit=50&offset=0&sort=year.json",
        encoding="utf-8",
    ) as f:
        assert response.json() == json.load(f)


def test_404():
    response = client.get("/movies/1")
    assert response.status_code == 404
