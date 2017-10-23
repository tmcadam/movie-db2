import unittest
import json
from nose.tools import assert_equals

import moviedb2
from moviedb2.database_helpers import drop_db, insert_timestamped_doc

class Moviedb2TestCase(unittest.TestCase):

    def test_get_movies(self):
        rv = self.app.get('/moviesdb2/filenames')
        assert rv.status_code == 200

    def test_can_post_new_hash_if_new(self):
        data = {"hash": "hash1", "filename": "test.avi"}
        rv = self.app.post('/moviesdb2/api/v1.0/filenames',
                           data=json.dumps(data),
                           content_type='application/json')
        assert_equals(rv.status_code, 200)
        assert_equals(self.db.movie_names.count(), 1)

    def test_returns_400_if_hash_already_in_db(self):
        #insert_timestamped_doc(self.db.movie_names, data)
        data = {"hash": "hash1", "filename": "test.avi"}
        rv = self.app.post('/moviesdb2/api/v1.0/filenames',
                           data=json.dumps(data),
                           content_type='application/json')
        assert_equals(rv.status_code, 200)
        assert_equals(self.db.movie_names.count(), 1)

        rv = self.app.post('/moviesdb2/api/v1.0/filenames',
                           data=json.dumps(data),
                           content_type='application/json')
        assert_equals(rv.status_code, 400)
        assert_equals(self.db.movie_names.count(), 1)

    def test_setUp_sets_the_right_database_for_tests(self):
        assert_equals(self.db.name, "movies-test")

    def setUp(self):
        self.app = moviedb2.app.test_client()
        moviedb2.app.config.from_object('config.TestingConfig')
        self.db = moviedb2.connect_db(moviedb2.app)

    def tearDown(self):
        drop_db(moviedb2.app, "movies-test")
