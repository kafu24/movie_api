from fastapi.testclient import TestClient

from src.api.server import app
from src import database as db
from src.datatypes import Conversation, Line
import sqlalchemy

client = TestClient(app)


def test_post_conversation_01():
    # Post then get on the conv_id and hope it comes as expected then delete it
    with db.engine.connect() as conn:
        result = conn.execute(
            sqlalchemy.select(
                sqlalchemy.sql.functions.max(db.lines.c.line_id),
            )
        )
        cur_id = result.first().max_1 + 1
        result = conn.execute(
            sqlalchemy.select(
                sqlalchemy.sql.functions.max(db.conversations.c.conversation_id),
            )
        )
        conv_id = result.first().max_1 + 1

    response = client.post(
        "/movies/13/conversations/",
        headers={"Content-Type": "application/json"},
        json={
            "character_1_id": 208,
            "character_2_id": 209,
            "lines": [
                {
                    "character_id": 208,
                    "line_text": "test"
                },
                {
                    "character_id": 209,
                    "line_text": "shut up"
                },
                {
                    "character_id": 208,
                    "line_text": "the hell you just say to me?"
                }
            ]
        }
    )
    assert response.status_code == 200
    assert response.json()["conversation_id"] == conv_id

    conv_id = response.json()["conversation_id"]
    get_request = "/lines/conversations/" + str(conv_id)
    response = client.get(get_request)
    assert response.status_code == 200

    expected_response = [
        {
            "line_id": cur_id,
            "character": "MURDOCK",
            "movie": "airplane!",
            "line_text": "test",
        },
        {
            "line_id": cur_id + 1,
            "character": "OVEUR",
            "movie": "airplane!",
            "line_text": "shut up"
        },
        {
            "line_id": cur_id + 2,
            "character": "MURDOCK",
            "movie": "airplane!",
            "line_text": "the hell you just say to me?",
        },
    ]

    assert response.json() == expected_response

    with db.engine.begin() as conn:
        result = conn.execute(
            sqlalchemy.delete(
                db.lines,
            )
            .where(db.lines.c.conversation_id == conv_id)
        )
        result = conn.execute(
            sqlalchemy.delete(
                db.conversations,
            )
            .where(db.conversations.c.conversation_id == conv_id)
        )


def test_post_conversration_404():
    # Movie not found
    response = client.post(
        "/movies/11231287312873612833/conversations/",
        headers={"Content-Type": "application/json"},
        json={
            "character_1_id": 208,
            "character_2_id": 209,
            "lines": [
                {
                    "character_id": 208,
                    "line_text": "test"
                },
                {
                    "character_id": 209,
                    "line_text": "shut up"
                },
                {
                    "character_id": 208,
                    "line_text": "the hell you just say to me?"
                }
            ]
        }
    )
    assert response.status_code == 404

    # Character not found
    response = client.post(
        "/movies/13/conversations/",
        headers={"Content-Type": "application/json"},
        json={
            "character_1_id": 20839182731923719823,
            "character_2_id": 209,
            "lines": [
                {
                    "character_id": 208,
                    "line_text": "test"
                },
                {
                    "character_id": 209,
                    "line_text": "shut up"
                },
                {
                    "character_id": 208,
                    "line_text": "the hell you just say to me?"
                }
            ]
        }
    )
    assert response.status_code == 404

    # Identical characters (404 because it's too annoying to make this a 400)
    response = client.post(
        "/movies/13/conversations/",
        headers={"Content-Type": "application/json"},
        json={
            "character_1_id": 208,
            "character_2_id": 208,
            "lines": [
                {
                    "character_id": 208,
                    "line_text": "test"
                },
                {
                    "character_id": 209,
                    "line_text": "shut up"
                },
                {
                    "character_id": 208,
                    "line_text": "the hell you just say to me?"
                }
            ]
        }
    )
    assert response.status_code == 404


def test_post_conversation_400():
    # Wrong characters in line
    response = client.post(
        "/movies/13/conversations/",
        headers={"Content-Type": "application/json"},
        json={
            "character_1_id": 208,
            "character_2_id": 209,
            "lines": [
                {
                    "character_id": 208,
                    "line_text": "test"
                },
                {
                    "character_id": 209,
                    "line_text": "shut up"
                },
                {
                    "character_id": 7414,
                    "line_text": "the hell you just say to me?"
                }
            ]
        }
    )
    assert response.status_code == 400

    