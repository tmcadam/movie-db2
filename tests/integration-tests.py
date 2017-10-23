import unittest
import json
import hashlib
from nose.tools import assert_equals

class IntegrationTestCase(unittest.TestCase):

        def get_1mb_checksum( self, filename ):
            with open(filename, 'rb') as f:
                md5 = hashlib.md5(f.read(1048576))
            return md5.hexdigest()

        def setUp(self):
            self.file1_hash = self.get_1mb_checksum("/home/tmcadam/Tools/movie-db2/tests/movies-folder/movie1.avi")
            self.file2_hash = self.get_1mb_checksum("/home/tmcadam/Tools/movie-db2/tests/movies-folder/movie2.avi")
            self.file3_hash = self.get_1mb_checksum("/home/tmcadam/Tools/movie-db2/tests/movies-folder/movie3.avi")

        def tearDown(self):
            pass

        def test_helloworld(self):
            with open("/home/tmcadam/Tools/movie-db2/client/movie_data.json", 'r') as f:
                data = json.load(f)
            assert_equals(data[self.file1_hash]["status"], "sent")
            assert_equals(data[self.file2_hash]["status"], "sent")
            assert_equals(data[self.file3_hash]["status"], "sent")
