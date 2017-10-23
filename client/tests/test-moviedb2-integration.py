import os
import unittest
import shutil
from pathlib import Path
from nose.tools import assert_equals
import requests_mock

from moviedb2 import moviedb2

POST_SERVER_URL = "http://localhost:5000/moviesdb2/api/v1.0/filenames"

class Moviedb2IntegrationTestCase(unittest.TestCase):

    # an integration test of every other function
    def test_monitor_folder_responds_to_new_files_in_folder(self):
        os.mkdir(self.test_folder)
        with requests_mock.mock() as m:
            # empty folder
            m.post(POST_SERVER_URL, status_code=200)
            folder_stats = moviedb2.monitor_folder(self.test_folder, self.tmp_movie_data_path)
            assert_equals(folder_stats["sent"], 0)
            assert_equals(folder_stats["found"], 0)
            assert_equals(folder_stats["count"], 0)
            # 2 files added but the server is not accepting the files being sent
            m.post(POST_SERVER_URL, status_code=404)
            Path(os.path.join(self.test_folder, "movie1.avi")).touch()
            Path(os.path.join(self.test_folder, "movie2.avi")).touch()
            m.post(POST_SERVER_URL, status_code=404)
            folder_stats = moviedb2.monitor_folder(self.test_folder, self.tmp_movie_data_path)
            assert_equals(folder_stats["sent"], 0)
            assert_equals(folder_stats["found"], 2)
            assert_equals(folder_stats["count"], 2)
            # after another run the 2 files aren't classed as newly found
            folder_stats = moviedb2.monitor_folder(self.test_folder, self.tmp_movie_data_path)
            assert_equals(folder_stats["sent"], 0)
            assert_equals(folder_stats["found"], 0)
            assert_equals(folder_stats["count"], 2)
            # server is accepting the files
            m.post(POST_SERVER_URL, status_code=200)
            folder_stats = moviedb2.monitor_folder(self.test_folder, self.tmp_movie_data_path)
            assert_equals(folder_stats["sent"], 2)
            assert_equals(folder_stats["found"], 0)
            assert_equals(folder_stats["count"], 2)
            # add a third file while the server is up
            Path(os.path.join(self.test_folder, "movie3.avi")).touch()
            folder_stats = moviedb2.monitor_folder(self.test_folder, self.tmp_movie_data_path)
            assert_equals(folder_stats["sent"], 1)
            assert_equals(folder_stats["found"], 1)
            assert_equals(folder_stats["count"], 3)
            # after another run the news and sents should disappear
            Path(os.path.join(self.test_folder, "movie3.avi")).touch()
            folder_stats = moviedb2.monitor_folder(self.test_folder, self.tmp_movie_data_path)
            assert_equals(folder_stats["sent"], 0)
            assert_equals(folder_stats["found"], 0)
            assert_equals(folder_stats["count"], 3)

    def setUp(self):
        self.test_folder = os.path.join("tests", "data" "test_movies")
        self.tmp_movie_data_path = os.path.join("tests", "data", "test-movie-data-modified.json")
        moviedb2.load_config ( "config.yml" )

    def tearDown(self):
        try:
            os.remove(self.tmp_movie_data_path)
        except OSError:
                pass
        if os.path.exists(self.test_folder):
            if os.path.isdir(self.test_folder):
                shutil.rmtree(self.test_folder)
            else:
                os.remove(self.test_folder)
