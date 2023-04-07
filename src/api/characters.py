import json
from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from operator import itemgetter

router = APIRouter()


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
    response = {}
    try:
        character = db.characters[str(id)]
        response["character_id"] = id
        response["character"] = character["name"]
        response["movie"] = db.movies[character["movie_id"]]["title"]
        # Gender and Age can be empty
        response["gender"] = character["gender"] if len(character["gender"]) != 0 else None
        response["top_conversations"] = []
        convos = query_convos_get_char(str(id))
        for convo in convos:
            conversation = {}
            conversation["character_id"] = int(convo[0])
            conversation["character"] = db.characters[convo[0]]["name"]
            conversation["gender"] = db.characters[convo[0]]["gender"] if len(db.characters[convo[0]]["gender"]) != 0 else None
            conversation["number_of_lines_together"] = int(convo[1])
            response["top_conversations"].append(conversation)
    except KeyError:
        raise HTTPException(status_code=404, detail="character not found")

    return response


def query_convos_get_char(char_id: str) -> list[tuple]:
    """
    Given a `char_id`, goes over the conversations database and returns
    a sorted list of tuples where each tuple is of the form:
        (character_id of other character talked to, number of lines in conversations)
    Sorted by descending order # of lines then by increasing `character_id`.
    """
    convos = {}
    for conversation in db.conversations:
        if conversation["character1_id"] == char_id:
            count = len(db.lines_con_id[conversation["conversation_id"]])
            convos[conversation["character2_id"]] = convos.get(conversation["character2_id"], 0) + count
        elif conversation["character2_id"] == char_id:
            count = len(db.lines_con_id[conversation["conversation_id"]])
            convos[conversation["character1_id"]] = convos.get(conversation["character1_id"], 0) + count
    return sorted(sorted(list(convos.items()), key=itemgetter(0)), key=itemgetter(1), reverse=True)


class character_sort_options(str, Enum):
    character = "character"
    movie = "movie"
    number_of_lines = "number_of_lines"


@router.get("/characters/", tags=["characters"])
def list_characters(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
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
    if limit < 0:
        # Professor's example gives 500 error code, but I believe this is more appropriate.
        raise HTTPException(442,"limit is negative")
    if offset < 0:
        raise HTTPException(442, "offset is negative")
    response = []
    for k, v in db.characters.items():
        if v["name"] == '':  # For some reason we don't include character with no name
            continue
        if name.upper() in v["name"].upper():
            character_response = {}
            character_response["character_id"] = int(v["character_id"])
            character_response["character"] = v["name"]
            character_response["movie"] = db.movies[v["movie_id"]]["title"]
            character_response["number_of_lines"] = len(db.lines_char_id[v["character_id"]])
            response.append(character_response)
    # To break tiebreakers
    response.sort(key=itemgetter("character_id"))
    if sort == character_sort_options.character:
        response.sort(key=itemgetter("character"))
    elif sort == character_sort_options.movie:
        response.sort(key=itemgetter("movie"))
    elif sort == character_sort_options.number_of_lines:
        response.sort(key=itemgetter("number_of_lines"), reverse=True)
    
    return response[offset:offset+limit]
