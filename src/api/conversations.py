from fastapi import APIRouter, HTTPException
from src import database as db
from pydantic import BaseModel
from typing import List
from datetime import datetime
import sqlalchemy


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
    stmt = (
        sqlalchemy.select(
            db.characters.c.character_id,
            db.characters.c.movie_id
        )
        .where(((db.characters.c.character_id == conversation.character_1_id)
                | (db.characters.c.character_id == conversation.character_2_id))
               & (db.characters.c.movie_id == movie_id))
    )

    with db.engine.begin() as conn:
        # Check if movie exists
        result = conn.execute(
            sqlalchemy.select(
                db.movies.c.movie_id,
            )
            .where(db.movies.c.movie_id == movie_id)
        )
        result = result.first()
        if result is None:
            raise HTTPException(status_code=404, detail="movie not found.")
        
        # Check if the characters exist for that movie
        result = conn.execute(stmt)
        characters = []
        for row in result:
            characters.append(row)
        if len(characters) != 2:
            raise HTTPException(status_code=404, detail="improper characters given.")

        # Get latest ids available
        result = conn.execute(
            sqlalchemy.select(
                sqlalchemy.sql.functions.max(db.lines.c.line_id),
            )
        )
        for row in result:
            cur_id = row.max_1 + 1
        
        result = conn.execute(
            sqlalchemy.select(
                sqlalchemy.sql.functions.max(db.conversations.c.conversation_id),
            )
        )
        for row in result:
            conv_id = row.max_1 + 1

        # Insert conversation_id into conversations first due to fkey
        result = conn.execute(
            sqlalchemy.insert(db.conversations)
            .values(conversation_id=conv_id,
                    character1_id=conversation.character_1_id,
                    character2_id=conversation.character_2_id,
                    movie_id=movie_id)
        )

        line_sort = 0
        for l in conversation.lines:
            line_sort += 1
            if (l.character_id != characters[0].character_id 
                and l.character_id != characters[1].character_id):
                raise HTTPException(status_code=400, detail="wrong character in lines.")
            result = conn.execute(
                sqlalchemy.insert(db.lines)
                .values(line_id=cur_id, 
                        character_id=l.character_id,
                        movie_id=movie_id, 
                        conversation_id=conv_id, 
                        line_sort=line_sort,
                        line_text=l.line_text)
            )
            cur_id += 1

    # db.logs.append({"post_call_time": datetime.now(), "movie_id_added_to": movie_id,
    #                 "conversation_id": conv_id})
    # db.upload_new_log()

    return {"conversation_id": conv_id}
