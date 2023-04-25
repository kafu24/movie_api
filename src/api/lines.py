from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from operator import itemgetter

router = APIRouter()

@router.get("/lines/{line_id}", tags=["lines"])
def get_line(line_id: int):
    """
    This endpoint returns a single line by its identifier. For each line it returns:
    * `line_id`: the internal id of the line
    * `line_text`: the text of the line
    * `character`: the name of the character speaking the line
    * `movie`: the title of the movie the line is from
    * `conversation_id`: the internal id of the conversation the line is from
    """
    response = {}
    try:
        line = db.lines[line_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="line not found")
    
    response["line_id"] = line_id
    response["line_text"] = line.line_text
    response["character"] = db.characters[line.c_id].name
    response["movie"] = db.movies[line.movie_id].title
    response["conversation_id"] = line.conv_id

    return response


@router.get("/lines/conversations/{conversation_id}", tags=["lines", "conversation"])
def get_conversation(conversation_id: int):
    """
    This endpoint creates a list of lines given a conversation id. The lines
    are sorted based on the internal `line_sort` value in ascending order.
    Each line is represented by a dictionary with keys:
    * `line_id`: the internal id of the line
    * `character`: the name of the character speaking the line
    * `movie`: the title of the movie the line is from
    * `line_text`: the text of the line
    """
    response = []
    try:
        conversation = db.conversations[conversation_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="conversation not found")
    
    items = list(filter(lambda l: conversation_id == l.conv_id, db.lines.values()))
    items.sort(key=lambda l: l.line_sort)
    for l in items:
        response.append(
            {
                "line_id": l.id,
                "character": db.characters[l.c_id].name,
                "movie": db.movies[l.movie_id].title,
                "line_text": l.line_text
            }
        )

    return response
    