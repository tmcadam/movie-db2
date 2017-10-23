from pymongo import MongoClient

client = MongoClient()
client.drop_database("movies-test")
