from pymongo import MongoClient

def connect_db(app):
    """Connects to the specific database."""
    client = MongoClient(app.config["DATABASE_HOST"], app.config["DATABASE_PORT"])
    return client[app.config["DATABASE_NAME"]]
