from fastapi.testclient import TestClient

from src.api.server import app
from src import database as db
from src.datatypes import Conversation, Line

client = TestClient(app)


def test_post_conversation_01():
    # Obviously this test has to be ran alone otherwise these values aren't 
    # actually expected.
    char_1_prev_num_lines = db.characters[208].num_lines
    char_2_prev_num_lines = db.characters[209].num_lines
    expected_conv_id = list(db.conversations.values())[-1].id + 1
    expected_line_ids = [list(db.lines.values())[-1].id + 1]
    expected_line_ids.append(expected_line_ids[-1] + 1)
    expected_line_ids.append(expected_line_ids[-1] + 1)
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

    assert response.json() == {"conversation_id": expected_conv_id}
    expected_conversation = Conversation(
        expected_conv_id,
        208,
        209,
        13,
        3
    )
    assert db.conversations[expected_conv_id] == expected_conversation
    expected_line_1 = Line(
        expected_line_ids[0],
        208,
        13,
        expected_conv_id,
        1,
        "test"
    )
    expected_line_2 = Line(
        expected_line_ids[1],
        209,
        13,
        expected_conv_id,
        2,
        "shut up"
    )
    expected_line_3 = Line(
        expected_line_ids[2],
        208,
        13,
        expected_conv_id,
        3,
        "the hell you just say to me?"
    )
    assert db.lines[expected_line_ids[0]] == expected_line_1
    assert db.lines[expected_line_ids[1]] == expected_line_2
    assert db.lines[expected_line_ids[2]] == expected_line_3
    assert db.characters[208].num_lines == char_1_prev_num_lines + 2
    assert db.characters[209].num_lines == char_2_prev_num_lines + 1

    # Clean up the stuff now
    db.characters[208].num_lines -= 2
    db.characters[209].num_lines -= 1
    del db.lines[expected_line_ids[0]]
    del db.lines[expected_line_ids[1]]
    del db.lines[expected_line_ids[2]]
    del db.conversations[expected_conv_id]


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


def test_post_conversation_400():
    # Identical characters
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
    assert response.status_code == 400

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

    