from fastapi import APIRouter, HTTPException
from src import database as db
from src.datatypes import Character, Movie, Conversation, Line
from pydantic import BaseModel
from typing import List
from datetime import datetime


# FastAPI is inferring what the request body should look like
# based on the following two classes.
class LinesJson(BaseModel):
    character_id: int
    line_text: str


class ConversationJson(BaseModel):
    character_1_id: int
    character_2_id: int
    lines: List[LinesJson]


router = APIRouter()


@router.post("/movies/{movie_id}/conversations/", tags=["movies"])
def add_conversation(movie_id: int, conversation: ConversationJson):
    """
    This endpoint adds a conversation to a movie. The conversation is represented
    by the two characters involved in the conversation and a series of lines between
    those characters in the movie.

    The endpoint ensures that all characters are part of the referenced movie,
    that the characters are not the same, and that the lines of a conversation
    match the characters involved in the conversation.

    Line sort is set based on the order in which the lines are provided in the
    request body.

    The endpoint returns the id of the resulting conversation that was created.
    """
    try:
        movie = db.movies[movie_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="movie not found.")
    
    try:
        c1 = db.characters[conversation.character_1_id]
        c2 = db.characters[conversation.character_2_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="character not found.")

    if c1.movie_id != movie.id or c2.movie_id != movie.id:
        raise HTTPException(status_code=404, detail="character not found in movie.")
    if c1 == c2:
        raise HTTPException(status_code=400, detail="identical characters given.")
    
    # Python 3.6+ preserves order in dict. This should get us unused ids, as long as
    # a new line or conversation isn't added to the database.
    cur_id = list(db.lines.values())[-1].id + 1
    while cur_id in db.lines.keys():
        cur_id += 1   

    conv_id = list(db.conversations.values())[-1].id + 1
    while conv_id in db.conversations.keys():
        conv_id += 1

    line_sort = 0
    lines = []
    for l in conversation.lines:
        line_sort += 1
        if l.character_id != c1.id and l.character_id != c2.id:
            raise HTTPException(status_code=400, detail="wrong character in lines.")
        new_line = Line(
            cur_id,
            l.character_id,
            movie_id,
            conv_id,
            line_sort,
            l.line_text
        )
        lines.append({
            "line_id": cur_id,
            "character_id": l.character_id,
            "movie_id": movie_id,
            "conversation_id": conv_id,
            "line_sort": line_sort,
            "line_text": l.line_text
        })
        # Hope nothing was added here otherwise we're overwriting something.
        db.lines[cur_id] = new_line
        db.characters[l.character_id].num_lines += 1
        cur_id += 1

    new_conversation = Conversation(
        conv_id,
        conversation.character_1_id,
        conversation.character_2_id,
        movie_id,
        line_sort
    )
    new_conversation_json = [{
        "conversation_id": conv_id,
        "character1_id": conversation.character_1_id,
        "character2_id": conversation.character_2_id,
        "movie_id": movie_id
    }]
    
    # Again, if something was added here we're overwriting something.
    db.conversations[conv_id] = new_conversation
    # I don't know what I'm doing.
    # db.upload_new_lines(lines)
    # db.upload_new_conversations(new_conversation_json)
    db.logs.append({"post_call_time": datetime.now(), "movie_id_added_to": movie_id})
    db.upload_new_log()

    return {"conversation_id": conv_id}
