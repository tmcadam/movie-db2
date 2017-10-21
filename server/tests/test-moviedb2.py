import moviedb2
import unittest
import json

class Moviedb2TestCase(unittest.TestCase):

    def setUp(self):
        self.app = moviedb2.app.test_client()

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
