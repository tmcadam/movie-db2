import unittest
import json
from nose.tools import assert_equals

import moviedb2

class Moviedb2TestCase(unittest.TestCase):

    def test_hello_world(self):
        rv = self.app.get('/')
        assert rv.status_code == 200
        assert b'Hello, World!' in rv.data

    def test_can_post_new_filename(self):
        data = {"filename": "somefilename"}
        rv = self.app.post('/moviesdb2/api/v1.0/filenames',
                           data=json.dumps(data),
                           content_type='application/json')
        assert rv.status_code == 200
        assert_equals(self.db.movie_filenames.count(), 1)

    def setUp(self):
        self.app = moviedb2.app.test_client()
        moviedb2.app.config.from_object('config.TestingConfig')
        self.db = moviedb2.connect_db(moviedb2.app)

    def tearDown(self):
        self.db.drop_collection("movie_filenames")
