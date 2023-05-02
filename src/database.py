import csv
import os
import io
from supabase import Client, create_client
import sqlalchemy
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

def database_connection_url():
    dotenv.load_dotenv()
    DB_USER: str = os.environ.get("POSTGRES_USER")
    DB_PASSWD = os.environ.get("POSTGRES_PASSWORD")
    DB_SERVER: str = os.environ.get("POSTGRES_SERVER")
    DB_PORT: str = os.environ.get("POSTGRES_PORT")
    DB_NAME: str = os.environ.get("POSTGRES_DB")
    return f"postgresql://{DB_USER}:{DB_PASSWD}@{DB_SERVER}:{DB_PORT}/{DB_NAME}"

# Create a new DB engine based on our connection string
engine = create_engine(database_connection_url())

metadata_obj = sqlalchemy.MetaData()
movies = sqlalchemy.Table("movies", metadata_obj, autoload_with=engine)
characters = sqlalchemy.Table("characters", metadata_obj, autoload_with=engine)
conversations = sqlalchemy.Table("conversations", metadata_obj, autoload_with=engine)
lines = sqlalchemy.Table("lines", metadata_obj, autoload_with=engine)

# # Reading in the log file from the supabase bucket
# log_csv = (
#     supabase.storage.from_("movie-api")
#     .download("movie_conversations_log.csv")
#     .decode("utf-8")
# )

# logs = []
# for row in csv.DictReader(io.StringIO(log_csv), skipinitialspace=True):
#     logs.append(row)


# # Writing to the log file and uploading to the supabase bucket
# def upload_new_log():
#     output = io.StringIO()
#     csv_writer = csv.DictWriter(
#         output, fieldnames=["post_call_time", "movie_id_added_to", "conversation_id"]
#     )
#     csv_writer.writeheader()
#     csv_writer.writerows(logs)
#     supabase.storage.from_("movie-api").upload(
#         "movie_conversations_log.csv",
#         bytes(output.getvalue(), "utf-8"),
#         {"x-upsert": "true"},
#     )
