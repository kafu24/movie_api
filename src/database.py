import csv
from collections import defaultdict
from src.datatypes import Character, Movie, Conversation, Line
import os
import io
from supabase import Client, create_client
from sqlalchemy import create_engine
import dotenv

# DO NOT CHANGE THIS TO BE HARDCODED. ONLY PULL FROM ENVIRONMENT VARIABLES.
dotenv.load_dotenv()
supabase_api_key = os.environ.get("SUPABASE_API_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

if supabase_api_key is None or supabase_url is None:
    raise Exception(
        "You must set the SUPABASE_API_KEY and SUPABASE_URL environment variables."
    )

supabase: Client = create_client(supabase_url, supabase_api_key)

sess = supabase.auth.get_session()

# TODO: Below is purely an example of reading and then writing a csv from supabase.
# You should delete this code for your working example.

# START PLACEHOLDER CODE

# Reading in the log file from the supabase bucket
log_csv = (
    supabase.storage.from_("movie-api")
    .download("movie_conversations_log.csv")
    .decode("utf-8")
)

logs = []
for row in csv.DictReader(io.StringIO(log_csv), skipinitialspace=True):
    logs.append(row)


# Writing to the log file and uploading to the supabase bucket
def upload_new_log():
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["post_call_time", "movie_id_added_to"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(logs)
    supabase.storage.from_("movie-api").upload(
        "movie_conversations_log.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )

# END PLACEHOLDER CODE

def upload_new_lines(new_lines):
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["line_id", "character_id", "movie_id", "conversation_id", "line_sort", "line_text"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(new_lines)
    supabase.storage.from_("movie-api").upload(
        "lines.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )

def upload_new_conversations(new_conversation):
    output = io.StringIO()
    csv_writer = csv.DictWriter(
        output, fieldnames=["conversation_id", "character1_id", "character2_id", "movie_id"]
    )
    csv_writer.writeheader()
    csv_writer.writerows(new_conversation)
    supabase.storage.from_("movie-api").upload(
        "conversations.csv",
        bytes(output.getvalue(), "utf-8"),
        {"x-upsert": "true"},
    )

def try_parse(type, val):
    try:
        return type(val)
    except ValueError:
        return None


movie_csv = (
    supabase.storage.from_("movie-api")
    .download("movies.csv")
    .decode("utf-8")
)

movies = {
    try_parse(int, row["movie_id"]): Movie(
        try_parse(int, row["movie_id"]),
        row["title"] or None,
        row["year"] or None,
        try_parse(float, row["imdb_rating"]),
        try_parse(int, row["imdb_votes"]),
        row["raw_script_url"] or None,
    )
    for row in csv.DictReader(io.StringIO(movie_csv), skipinitialspace=True)
}

characters_csv = (
    supabase.storage.from_("movie-api")
    .download("characters.csv")
    .decode("utf-8")
)

characters = {}
for row in csv.DictReader(io.StringIO(characters_csv), skipinitialspace=True):
    char = Character(
        try_parse(int, row["character_id"]),
        row["name"] or None,
        try_parse(int, row["movie_id"]),
        row["gender"] or None,
        try_parse(int, row["age"]),
        0,
    )
    characters[char.id] = char

conversations_csv = (
    supabase.storage.from_("movie-api")
    .download("conversations.csv")
    .decode("utf-8")
)

conversations = {}
for row in csv.DictReader(io.StringIO(conversations_csv), skipinitialspace=True):
    conv = Conversation(
        try_parse(int, row["conversation_id"]),
        try_parse(int, row["character1_id"]),
        try_parse(int, row["character2_id"]),
        try_parse(int, row["movie_id"]),
        0,
    )
    conversations[conv.id] = conv

lines_csv = (
    supabase.storage.from_("movie-api")
    .download("lines.csv")
    .decode("utf-8")
)

lines = {}
for row in csv.DictReader(io.StringIO(lines_csv), skipinitialspace=True):
    line = Line(
        try_parse(int, row["line_id"]),
        try_parse(int, row["character_id"]),
        try_parse(int, row["movie_id"]),
        try_parse(int, row["conversation_id"]),
        try_parse(int, row["line_sort"]),
        row["line_text"],
    )
    lines[line.id] = line
    c = characters.get(line.c_id)
    if c:
        c.num_lines += 1
    conv = conversations.get(line.conv_id)
    if conv:
        conv.num_lines += 1
