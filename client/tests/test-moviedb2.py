import os
import unittest
import shutil
from pathlib import Path
from nose.tools import assert_equals
import requests_mock

from moviedb2 import moviedb2

POST_SERVER_URL = "http://localhost:5000/moviesdb2/api/v1.0/filenames"

class Moviedb2TestCase(unittest.TestCase):

    # an integration test of every other function
    def test_monitor_folder_responds_to_new_files_in_folder(self):
        self.tearDown()
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

    def test_can_write_movie_data_to_file(self):
        moviedb2.load_movie_data( self.movie_data_path )
        moviedb2.add_new_movie( "filename4" )
        moviedb2.set_movie_sent( "filename4" )
        moviedb2.write_movie_data( self.tmp_movie_data_path ) # this is being tested
        moviedb2.load_movie_data( self.tmp_movie_data_path )
        assert not moviedb2.is_new_movie( "filename4" )
        assert moviedb2.is_movie_sent( "filename4" )

    def test_can_update_movie_data_when_movie_sent(self):
        moviedb2.load_movie_data( self.movie_data_path )
        assert not moviedb2.is_movie_sent ( "filename1" )
        moviedb2.set_movie_sent( "filename1" )
        assert moviedb2.is_movie_sent( "filename1" )

    def test_can_add_filename_to_movie_data_when_movie_found(self):
        moviedb2.load_movie_data( self.movie_data_path )
        moviedb2.add_new_movie( "filename4" )
        assert not moviedb2.is_new_movie( "filename4" )
        assert not moviedb2.is_movie_sent( "filename4" )

    def test_can_check_movie_data_to_see_if_movie_sent(self):
        moviedb2.load_movie_data( self.movie_data_path )
        assert not moviedb2.is_movie_sent( "filename1" )
        assert moviedb2.is_movie_sent( "filename2" )

    def test_can_check_movie_data_to_see_if_movie_found(self):
        moviedb2.load_movie_data( self.movie_data_path )
        assert moviedb2.is_new_movie( "filename4" )
        assert not moviedb2.is_new_movie( "filename1" )

    def test_load_movie_data_sets_empty_dict_if_no_file(self):
        moviedb2.load_movie_data( "some_non_existant_file.json" )
        data = moviedb2.MOVIE_DATA
        assert_equals(type(data).__name__, "dict")

    def test_can_read_movie_data_into_memory(self):
        moviedb2.load_movie_data( self.movie_data_path )
        data = moviedb2.MOVIE_DATA
        assert_equals(len(data), 3)
        assert "filename1" in data and data["filename1"]["status"] == "found"
        assert "filename2" in data and data["filename2"]["status"] == "sent"
        assert "filename3" in data and data["filename3"]["status"] == "send failed"

    def test_can_read_variables_from_config(self):
        assert moviedb2.load_config ( os.path.join("tests", "data", "test-config.yml") )
        config = moviedb2.CONFIG
        assert "PATH" in config and config["PATH"] == "/test path/movies/"
        assert "POST_SERVER_URL" in config and config["POST_SERVER_URL"] == "http://test-url.com"
        assert "FILE_EXTS" in config and len(config["FILE_EXTS"]) == 3 and config["FILE_EXTS"][0] == ".avi"


    def test_send_filename_returns_true_if_successful(self):
        with requests_mock.mock() as m:
            m.post(POST_SERVER_URL, status_code=200)
            assert moviedb2.send_filename_to_server('some_file_name')

    def test_send_filename_returns_false_if_unsuccessful(self):
        with requests_mock.mock() as m:
            m.post(POST_SERVER_URL, status_code=403)
            assert not moviedb2.send_filename_to_server('some_file_name')[0]

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
        self.tmp_movie_data_path = os.path.join("tests", "data", "test-movie-data-modified.json")
        self.movie_data_path = os.path.join("tests", "data", "test-movie-data.json")
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
        try:
            os.remove(self.tmp_movie_data_path)
        except OSError:
                pass
        if os.path.exists(self.test_folder):
            if os.path.isdir(self.test_folder):
                shutil.rmtree(self.test_folder)
            else:
                os.remove(self.test_folder)
