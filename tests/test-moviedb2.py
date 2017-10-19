import moviedb2
import unittest


class Moviedb2TestCase(unittest.TestCase):

    def setUp(self):
        self.app = moviedb2.app.test_client()

    def test_hello_world(self):
        rv = self.app.get('/')
        assert rv.status_code == 200
        assert b'Hello, World!' in rv.data

if __name__ == '__main__':
    unittest.main()
