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
        line = db.lines[str(line_id)]
    except KeyError:
        raise HTTPException(status_code=404, detail="line not found")
    
    response["line_id"] = line_id
    response["line_text"] = line["line_text"]
    response["character"] = db.characters[line["character_id"]]["name"]
    response["movie"] = db.movies[line["movie_id"]]["title"]
    response["conversation_id"] = int(line["conversation_id"])

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
        conversation = db.conversations[str(conversation_id)]
    except KeyError:
        raise HTTPException(status_code=404, detail="conversation not found")
    
    for c in sorted(db.lines_con_id[conversation["conversation_id"]], key=itemgetter("line_sort")):
        response.append(
            {
                "line_id": int(c["line_id"]),
                "character": db.characters[c["character_id"]]["name"],
                "movie": db.movies[c["movie_id"]]["title"],
                "line_text": c["line_text"]
            }
        )

    return response


@router.get("/lines/characters/{character_id}", tags=["lines", "characters"])
def get_character_lines(character_id: int):
    """
    This endpoint creates a list of all lines spoken by a character. The lines
    are in ascending order based on their line_id (aka chronologically).
    Each line is represented by a dictionary with keys:
    * `line_id`: the internal id of the line
    * `character`: the name of the character speaking the line
    * `movie`: the title of the movie the line is from
    * `conversation_id`: the internal id of the conversation the line is from
    * `line_text`: the text of the line
    """
    response = []
    try:
        lines = db.lines_char_id[str(character_id)]
    except KeyError:
        raise HTTPException(status_code=404, detail="character not found")
    
    # This should already be sorted, but it's not a big deal to be careful.
    lines.sort(key=itemgetter("line_id"))
    for line in lines:
        response.append(
            {
                "line_id": int(line["line_id"]),
                "character": db.characters[str(character_id)]["name"],
                "movie": db.movies[line["movie_id"]]["title"],
                "conversation_id": int(line["conversation_id"]),
                "line_text": line["line_text"]
            }
        )
    
    return response
    
    