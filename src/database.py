import csv
from collections import defaultdict

print("reading movies")

with open("movies.csv", mode="r", encoding="utf8") as csv_file:
    reader = csv.DictReader(csv_file, skipinitialspace=True)
    movies = {}
    for row in reader:
        movies[row["movie_id"]] = {k: v for k, v in row.items()}

print("reading characters")

with open("characters.csv", mode="r", encoding="utf8") as csv_file:
    reader = csv.DictReader(csv_file, skipinitialspace=True)
    characters = {}
    for row in reader:
        characters[row["character_id"]] = {k: v for k, v in row.items()}

print("reading conversations")

with open("conversations.csv", mode="r", encoding="utf8") as csv_file:
    reader = csv.DictReader(csv_file, skipinitialspace=True)
    conversations = {}
    for row in reader:
        conversations[row["conversation_id"]] = {k: v for k, v in row.items()}

print("reading lines")

with open("lines.csv", mode="r", encoding="utf8") as csv_file:
    reader = csv.DictReader(csv_file, skipinitialspace=True)
    lines = {}
    lines_con_id = defaultdict(list)
    lines_char_id = defaultdict(list)
    lines_movie_id = defaultdict(list)
    # Dictionary to easily search up lines of a conversation by its id
    # and dictionary to easily search up lines by a character by their id
    # and movies by their id... This really is the most important file, huh?
    # Let's just assume there's going to be more movies for characters in the future :^)
    for row in reader:
        lines[row["line_id"]] = {k: v for k, v in row.items()}
        lines_con_id[row["conversation_id"]].append({k: v for k, v in row.items()})
        lines_char_id[row["character_id"]].append({k: v for k, v in row.items()})
        lines_movie_id[row["movie_id"]].append({k: v for k, v in row.items()})
