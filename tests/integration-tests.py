import unittest
import json
import hashlib
import time
import os
from nose.tools import assert_equals
from selenium import webdriver
from pymongo import MongoClient

dbclient = MongoClient()

class IntegrationTestCase(unittest.TestCase):
        filenames = list()

        def get_1mb_checksum( self, filename ):
            with open(filename, 'rb') as f:
                md5 = hashlib.md5(f.read(1048576))
            return md5.hexdigest()

        def setUp(self):
            dbclient.drop_database("movies-test")
            for c in [1,2,3]:
                filename = '/home/tmcadam/Tools/movie-db2/tests/movies-folder/movie{}.avi'.format(c)
                self.filenames.append(filename)
                with open(filename, 'wb') as f:
                    f.write(os.urandom(2097152)) #2mb
            self.file1_hash = self.get_1mb_checksum("/home/tmcadam/Tools/movie-db2/tests/movies-folder/movie1.avi")
            self.file2_hash = self.get_1mb_checksum("/home/tmcadam/Tools/movie-db2/tests/movies-folder/movie2.avi")
            self.file3_hash = self.get_1mb_checksum("/home/tmcadam/Tools/movie-db2/tests/movies-folder/movie3.avi")
            time.sleep(2)

        def tearDown(self):
            for f in self.filenames:
                os.remove(f)

        def test_helloworld(self):
            with open("/home/tmcadam/Tools/movie-db2/client/movie_data.json", 'r') as f:
                data = json.load(f)
            assert_equals(data[self.file1_hash]["status"], "sent")
            assert_equals(data[self.file2_hash]["status"], "sent")
            assert_equals(data[self.file3_hash]["status"], "sent")


class BrowserTestCase(unittest.TestCase):
    filenames = list()
    @classmethod
    def setUpClass(cls):
        cls.driver = webdriver.PhantomJS()

    def setUp(self):
        dbclient.drop_database("movies-test")
        for c in [1,2,3]:
            filename = '/home/tmcadam/Tools/movie-db2/tests/movies-folder/movie{}.avi'.format(c)
            self.filenames.append(filename)
            with open(filename, 'wb') as f:
                f.write(os.urandom(2097152)) #2mb
        time.sleep(2)

    def test_3_movies_have_been_loaded_to_server(self):

        self.driver.set_window_size(1120, 550)
        self.driver.get('http://localhost:5000/moviesdb2/filenames')
        self.assertEqual(self.driver.title,'Movies')
        elements = self.driver.find_elements_by_css_selector('li')
        self.assertEqual(len(elements), 3)

    def tearDown(self):
        for f in self.filenames:
            os.remove(f)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
