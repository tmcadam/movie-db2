from moviedb2 import moviedb2
import unittest


class Moviedb2TestCase(unittest.TestCase):

    def test_hello_world(self):
        assert moviedb2.hello_world() == 200
