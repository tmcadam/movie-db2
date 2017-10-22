from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import datetime

def create_schema(db):
    if "movie_names" not in db.collection_names():
        db.create_collection("movie_names")
        db.movie_names.create_index("filename", unique=True)

def connect_db(app):
    """Connects to the specific database."""
    client = MongoClient(app.config["DATABASE_HOST"], app.config["DATABASE_PORT"])
    db = client[app.config["DATABASE_NAME"]]
    create_schema(db)
    return db

def insert_timestamped_doc(collection, data):
    data["created_at"] = datetime.datetime.now()
    data["updated_at"] = datetime.datetime.now()
    try:
        collection.insert_one(data)
        return True
    except DuplicateKeyError as e:
        return False
