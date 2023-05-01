import json
from fastapi import APIRouter, HTTPException
from enum import Enum
from collections import Counter, defaultdict
from operator import itemgetter
from fastapi.params import Query
from src import database as db
import sqlalchemy

router = APIRouter()


def get_top_conv_characters(character):
    c_id = character.id
    movie_id = character.movie_id
    all_convs = filter(
        lambda conv: conv.movie_id == movie_id
        and (conv.c1_id == c_id or conv.c2_id == c_id),
        db.conversations.values(),
    )
    line_counts = Counter()

    for conv in all_convs:
        other_id = conv.c2_id if conv.c1_id == c_id else conv.c1_id
        line_counts[other_id] += conv.num_lines

    return line_counts.most_common()


@router.get("/characters/{id}", tags=["characters"])
def get_character(id: int):
    """
    This endpoint returns a single character by its identifier. For each character
    it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `gender`: The gender of the character.
    * `top_conversations`: A list of characters that the character has the most
      conversations with. The characters are listed in order of the number of
      lines together. These conversations are described below.

    Each conversation is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `gender`: The gender of the character.
    * `number_of_lines_together`: The number of lines the character has with the
      originally queried character.
    """
    stmt = (
        sqlalchemy.select(
            db.characters.c.character_id,
            db.characters.c.name,
            db.movies.c.title,
            db.characters.c.gender,
        )
        .where(db.characters.c.character_id == id)
        .join(db.movies, db.characters.c.movie_id == db.movies.c.movie_id)
        .group_by(db.characters.c.character_id, db.movies.c.title)
    )

    stmt2 = (
        sqlalchemy.select(
            db.conversations.c.conversation_id,
            db.characters.c.character_id,
            db.conversations.c.character1_id,
            db.conversations.c.character2_id,
            sqlalchemy.func.count(db.lines.c.character_id).label("num_lines")
        )
        .where((db.conversations.c.character2_id == id) | (db.conversations.c.character1_id == id))
        .join(db.characters, (db.conversations.c.character1_id == db.characters.c.character_id))
        .join(db.lines, db.lines.c.conversation_id == db.conversations.c.conversation_id)
        .group_by(db.characters.c.character_id, db.conversations.c.conversation_id)
    )

    with db.engine.connect() as conn:
        result = conn.execute(stmt) # Should only return one row
        character_row = result.first()
        if character_row is None:
            raise HTTPException(status_code=404, detail="character not found.")

        result2 = conn.execute(stmt2)
        count_dict = defaultdict(int)
        for row in result2:
            char = row.character2_id if row.character1_id == id else row.character1_id
            count_dict[char] += row.num_lines

        result3 = conn.execute(
            sqlalchemy.select(
                db.characters.c.character_id,
                db.characters.c.name,
                db.characters.c.gender,
            )
            .where(db.characters.c.character_id.in_(list(count_dict.keys())))
            .order_by(db.characters.c.character_id)
        )
        top_conversations = []
        for row in result3:
            top_conversations.append(
                {
                    "character_id": row.character_id,
                    "character": row.name,
                    "gender": row.gender,
                    "number_of_lines_together": count_dict[row.character_id],
                }
            )
        # Result3 is already ordered by id. Sort by num_lines should still preserve that order.
        top_conversations.sort(key=itemgetter("number_of_lines_together"), reverse=True)
        json = {
            "character_id": id,
            "character": character_row.name,
            "movie": character_row.title,
            "gender": character_row.gender,
            "top_conversations": top_conversations,
        }

    return json


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = Query(50, ge=1, le=250),
    offset: int = Query(0, ge=0),
    sort: character_sort_options = character_sort_options.character,
):
    """
    This endpoint returns a list of characters. For each character it returns:
    * `character_id`: the internal id of the character. Can be used to query the
      `/characters/{character_id}` endpoint.
    * `character`: The name of the character.
    * `movie`: The movie the character is from.
    * `number_of_lines`: The number of lines the character has in the movie.

    You can filter for characters whose name contains a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `character` - Sort by character name alphabetically.
    * `movie` - Sort by movie title alphabetically.
    * `number_of_lines` - Sort by number of lines, highest to lowest.

    The `limit` and `offset` query
    parameters are used for pagination. The `limit` query parameter specifies the
    maximum number of results to return. The `offset` query parameter specifies the
    number of results to skip before returning results.
    """
    if sort is character_sort_options.character:
        order_by = db.characters.c.name
    elif sort is character_sort_options.movie:
        order_by = db.movies.c.title
    elif sort is character_sort_options.number_of_lines:
        order_by = sqlalchemy.desc(
            sqlalchemy.func.count(db.lines.c.character_id).label("count"))
    else:
        assert False

    stmt = (
        sqlalchemy.select(
            db.characters.c.character_id,
            db.characters.c.name,
            db.movies.c.title,
            sqlalchemy.func.count(db.lines.c.character_id).label("num_lines"),
        )
        .join(db.lines, db.characters.c.character_id == db.lines.c.character_id)
        .join(db.movies, db.characters.c.movie_id == db.movies.c.movie_id)
        .group_by(db.characters.c.character_id, db.movies.c.title)
        .limit(limit)
        .offset(offset)
        .order_by(order_by, db.characters.c.character_id)
    )

    # filter only if name parameter is passed
    if name != "":
        stmt = stmt.where(db.characters.c.name.ilike(f"%{name}%"))

    with db.engine.connect() as conn:
        result = conn.execute(stmt)
        json = []
        for row in result:
            json.append(
                {
                    "character_id": row.character_id,
                    "character": row.name,
                    "movie": row.title,
                    "number_of_lines": row.num_lines,
                }
            )

    return json


@router.get("/characters/{character_id}/lines", tags=["lines", "characters"])
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
        lines = db.characters[character_id]
    except KeyError:
        raise HTTPException(status_code=404, detail="character not found")
    
    items = list(filter(lambda l: character_id == l.c_id, db.lines.values()))
    items.sort(key=lambda l: l.id)
    for line in items:
        response.append(
            {
                "line_id": line.id,
                "character": db.characters[character_id].name,
                "movie": db.movies[line.movie_id].title,
                "conversation_id": line.conv_id,
                "line_text": line.line_text
            }
        )
    
    return response
