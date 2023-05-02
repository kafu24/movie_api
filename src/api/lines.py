from fastapi import APIRouter, HTTPException
from src import database as db
import sqlalchemy

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
    stmt = (
        sqlalchemy.select(
            db.lines.c.line_id,
            db.lines.c.line_text,
            db.characters.c.name,
            db.movies.c.title,
            db.lines.c.conversation_id,
        )
        .where(db.lines.c.line_id == line_id)
        .join(db.characters, db.characters.c.character_id == db.lines.c.character_id)
        .join(db.movies, db.movies.c.movie_id == db.lines.c.movie_id)
        .group_by(db.lines.c.line_id, db.characters.c.character_id, db.movies.c.movie_id)
        .order_by(db.lines.c.line_id)
    )
    response = None
    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        for row in result:
            response = {
                "line_id": row.line_id,
                "line_text": row.line_text,
                "character": row.name,
                "movie": row.title,
                "conversation_id": row.conversation_id,
            }

    if response is None:
        raise HTTPException(status_code=404, detail="line not found")

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

    stmt = (
        sqlalchemy.select(
            db.lines.c.line_id,
            db.characters.c.name,
            db.movies.c.title,
            db.lines.c.line_text,
        )
        .where(db.lines.c.conversation_id == conversation_id)
        .join(db.characters, db.characters.c.character_id == db.lines.c.character_id)
        .join(db.movies, db.movies.c.movie_id == db.lines.c.movie_id)
        .group_by(db.lines.c.line_id, db.characters.c.character_id, db.movies.c.movie_id)
        .order_by(db.lines.c.line_sort)
    )

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        for row in result:
            response.append(
                {
                    "line_id": row.line_id,
                    "character": row.name,
                    "movie": row.title,
                    "line_text": row.line_text,
                }
            )

    if not response:
        raise HTTPException(status_code=404, detail="conversation not found")
    
    return response
    