import os
import unittest
import shutil
from pathlib import Path
from nose.tools import assert_equals
import requests_mock

from moviedb2 import moviedb2

POST_SERVER_URL = "http://localhost:5000/moviesdb2/api/v1.0/filenames"

class Moviedb2TestCase(unittest.TestCase):

    def test_can_read_variables_from_config(self):
        assert moviedb2.load_config ( os.path.join("tests", "data", "test-config.yml") )
        config = moviedb2.CONFIG
        assert "PATH" in config and config["PATH"] == "/test path/movies/"
        assert "POST_SERVER_URL" in config and config["POST_SERVER_URL"] == "http://test-url.com"
        assert "FILE_EXTS" in config and len(config["FILE_EXTS"]) == 3 and config["FILE_EXTS"][0] == ".avi"

    def test_monitor__folder_responds_to_new_file_in_folder(self):
        with requests_mock.mock() as m:
            m.post(POST_SERVER_URL, status_code=200)
            Path(os.path.join(self.test_folder, "blah.avi")).touch()
            assert_equals(moviedb2.monitor_folder(self.test_folder), 2)
        self.tearDown()
        os.mkdir(self.test_folder)
        assert_equals(moviedb2.monitor_folder(self.test_folder), 0)

    def test_send_filename_returns_true_if_successful(self):
        with requests_mock.mock() as m:
            m.post(POST_SERVER_URL, status_code=200)
            assert moviedb2.send_filename_to_server('some_file_name')

    def test_send_filename_returns_false_if_unsuccessful(self):
        with requests_mock.mock() as m:
            m.post(POST_SERVER_URL, status_code=403)
            assert not moviedb2.send_filename_to_server('some_file_name')

    def test_get_files_without_id_returns_subset_of_files(self):
        Path(os.path.join(self.test_folder, "blah {1980}.avi")).touch() # this one has an invalid IMDB id + 1 in the setUp = 2
        files = moviedb2.get_files_without_id(moviedb2.get_files(self.test_folder))
        assert_equals(len(files), 2)

    def test_get_files_returns_all_movie_files(self):
        files = moviedb2.get_files(self.test_folder)
        assert len(files) == 3
        for f in self.files:
            assert f in files

    def test_get_files_excludes_non_movie_files(self):
        Path(os.path.join(self.test_folder, "test1.sub")).touch()
        files = moviedb2.get_files(self.test_folder)
        assert_equals(len(files), 3)

    def test_get_files_returns_none_if_empty(self):
        self.tearDown()
        os.mkdir(self.test_folder)
        assert not moviedb2.get_files(self.test_folder)

    def test_check_folder_exists_returns_true_if_folder_exists(self):
        assert moviedb2.check_folder_exists(self.test_folder)

    def test_check_folder_exists_returns_false_if_no_folder(self):
        shutil.rmtree(self.test_folder)
        assert not moviedb2.check_folder_exists(self.test_folder)

    def test_check_folder_exists_return_false_if_file_not_folder(self):
        shutil.rmtree(self.test_folder)
        Path(self.test_folder).touch()
        assert not moviedb2.check_folder_exists(self.test_folder)

    def setUp(self):
        moviedb2.load_config ( "config.yml" )
        self.test_folder = os.path.join("tests", "data" "test_movies")
        self.files = [os.path.join(self.test_folder, "test1 {tt1234567}.avi"),
                        os.path.join(self.test_folder, "A", "test2 {tt2345678}.mp4"),
                        os.path.join(self.test_folder, "B", "test3.mkv")]
        os.mkdir(self.test_folder)
        os.mkdir(os.path.join(self.test_folder, "A"))
        os.mkdir(os.path.join(self.test_folder, "B"))
        for f in self.files:
            Path(f).touch()

    def tearDown(self):
        if os.path.exists(self.test_folder):
            if os.path.isdir(self.test_folder):
                shutil.rmtree(self.test_folder)
            else:
                os.remove(self.test_folder)

if __name__ == '__main__':
    unittest.main()
