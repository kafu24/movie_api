from fastapi import APIRouter, HTTPException
from enum import Enum
from src import database as db
from operator import itemgetter

router = APIRouter()


# include top 3 actors by number of lines
@router.get("/movies/{movie_id}", tags=["movies"])
def get_movie(movie_id: str):
    """
    This endpoint returns a single movie by its identifier. For each movie it returns:
    * `movie_id`: the internal id of the movie.
    * `title`: The title of the movie.
    * `top_characters`: A list of characters that are in the movie. The characters
      are ordered by the number of lines they have in the movie. The top five
      characters are listed.

    Each character is represented by a dictionary with the following keys:
    * `character_id`: the internal id of the character.
    * `character`: The name of the character.
    * `num_lines`: The number of lines the character has in the movie.

    """
    response = {}
    try:
        movie = db.movies[movie_id]
        response["movie_id"] = int(movie_id)
        response["title"] = movie["title"]
        response["top_characters"] = []
        characters = query_lines_get_movie(movie_id)
        for character in characters:
            chara_dict = {}
            chara_dict["character_id"] = int(character[0])
            chara_dict["character"] = db.characters[character[0]]["name"]
            chara_dict["num_lines"] = int(character[1])
            response["top_characters"].append(chara_dict)
    except KeyError:
        raise HTTPException(status_code=404, detail="movie not found")

    return response


def query_lines_get_movie(movie_id: str):
    """
    Given a `movie_id`, queries the line database with that id to count the number
    of lines each character has in the movie. Creates a list of tuples in the form:
        (character_id, number of lines they had)
    Sorted by descending # of lines then by increasing `character_id`.
    Only returns the top 5.
    """
    characters = {}
    for line in db.lines_movie_id[movie_id]:
        characters[line["character_id"]] = characters.get(line["character_id"], 0) + 1
    return sorted(sorted(list(characters.items()), key=itemgetter(0)), key=itemgetter(1), reverse=True)[:5]


class movie_sort_options(str, Enum):
    movie_title = "movie_title"
    year = "year"
    rating = "rating"


# Add get parameters
@router.get("/movies/", tags=["movies"])
def list_movies(
    name: str = "",
    limit: int = 50,
    offset: int = 0,
    sort: movie_sort_options = movie_sort_options.movie_title,
):
    """
    This endpoint returns a list of movies. For each movie it returns:
    * `movie_id`: the internal id of the movie. Can be used to query the
      `/movies/{movie_id}` endpoint.
    * `movie_title`: The title of the movie.
    * `year`: The year the movie was released.
    * `imdb_rating`: The IMDB rating of the movie.
    * `imdb_votes`: The number of IMDB votes for the movie.

    You can filter for movies whose titles contain a string by using the
    `name` query parameter.

    You can also sort the results by using the `sort` query parameter:
    * `movie_title` - Sort by movie title alphabetically.
    * `year` - Sort by year of release, earliest to latest.
    * `rating` - Sort by rating, highest to lowest.

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
    for k, v in db.movies.items():
        if name.upper() in v["title"].upper():
            movie_response = {}
            movie_response["movie_id"] = int(v["movie_id"])
            movie_response["movie_title"] = v["title"]
            movie_response["year"] = v["year"]
            movie_response["imdb_rating"] = float(v["imdb_rating"])
            movie_response["imdb_votes"] = int(v["imdb_votes"])
            response.append(movie_response)
    # To break tiebreakers
    response.sort(key=itemgetter("movie_id"))
    if sort == movie_sort_options.movie_title:
        response.sort(key=itemgetter("movie_title"))
    elif sort == movie_sort_options.year:
        response.sort(key=itemgetter("year"))
    elif sort == movie_sort_options.rating:
        response.sort(key=itemgetter("imdb_rating"), reverse=True)
    
    return response[offset:offset+limit]

