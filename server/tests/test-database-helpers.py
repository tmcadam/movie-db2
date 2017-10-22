import unittest
from nose.tools import raises, assert_equals
from pymongo.errors import DuplicateKeyError

from moviedb2.database_helpers import connect_db, insert_timestamped_doc
from config import TestingConfig

class MockApp:
    config = {
            "DATABASE_HOST": TestingConfig.DATABASE_HOST,
            "DATABASE_PORT": TestingConfig.DATABASE_PORT,
            "DATABASE_NAME": TestingConfig.DATABASE_NAME
        }

class Moviedb2TestCase(unittest.TestCase):

    @raises(DuplicateKeyError)
    def test_cannot_add_dupicate_filename_to_db(self):
        data = {"filename": "test1.avi"}
        self.db.movie_names.insert_one(data)
        self.db.movie_names.insert_one(data)

    def test_can_insert_movie_filename_to_db(self):
        data = {"filename": "test1.avi"}
        self.db.movie_names.insert_one(data)
        assert_equals(self.db.movie_names.count(), 1)

    def test_insert_timestamped_returns_true_and_adds_timestamps(self):
        data = {"filename": "test1.avi"}
        assert insert_timestamped_doc(self.db.movie_names,data)
        assert_equals(self.db.movie_names.count(), 1)
        doc = self.db.movie_names.find_one()
        assert "created_at" in doc.keys()
        assert "updated_at" in doc.keys()

    def test_insert_timestamps_returns_false_if_filename_exists(self):
        data = {"filename": "test1.avi"}
        assert insert_timestamped_doc(self.db.movie_names, data)
        assert not insert_timestamped_doc(self.db.movie_names, data)
        assert_equals(self.db.movie_names.count(), 1)

    def setUp(self):
        app = MockApp()
        self.db = connect_db(app)

    def tearDown(self):
        self.db.drop_collection("movie_names")
