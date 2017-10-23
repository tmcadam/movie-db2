import os
import unittest
import shutil
from pathlib import Path
from nose.tools import assert_equals
import requests_mock
import json

from moviedb2 import moviedb2

POST_SERVER_URL = "http://localhost:5000/moviesdb2/api/v1.0/filenames"

class Moviedb2TestCase(unittest.TestCase):

    def test_get_checksum_1mb_returns_checksum(self):
        checksum_file = os.path.join('tests','data','checksum-test.avi')
        expected_checksum = "3e9c3a8b73eab486bda7330cff4e0195" # calced using md5sum program in Ubuntu
        assert_equals( moviedb2.get_1mb_checksum(checksum_file), expected_checksum )

    def test_can_write_movie_data_to_file(self):
        moviedb2.load_movie_data( self.movie_data_path )
        self.make_file(self.new_file)
        hash = moviedb2.get_1mb_checksum (self.new_file)
        moviedb2.add_new_movie( self.new_file, hash  )
        moviedb2.set_movie_sent( hash )
        moviedb2.write_movie_data( self.tmp_movie_data_path ) # this is being tested
        moviedb2.load_movie_data( self.tmp_movie_data_path )
        assert not moviedb2.is_new_movie( hash )
        assert moviedb2.is_movie_sent( hash )

    def test_can_update_movie_data_when_movie_sent(self):
        moviedb2.load_movie_data( self.movie_data_path )
        assert not moviedb2.is_movie_sent ( self.files[0]["hash"] )
        moviedb2.set_movie_sent( self.files[0]["hash"] )
        assert moviedb2.is_movie_sent( self.files[0]["hash"] )

    def test_can_add_filename_to_movie_data_when_movie_found(self):
        moviedb2.load_movie_data( self.movie_data_path )
        self.make_file(self.new_file)
        hash = moviedb2.get_1mb_checksum (self.new_file)
        moviedb2.add_new_movie( self.new_file, hash  )
        assert not moviedb2.is_new_movie( hash )
        assert not moviedb2.is_movie_sent( hash )

    def test_can_check_movie_data_to_see_if_movie_sent(self):
        moviedb2.load_movie_data( self.movie_data_path )
        assert not moviedb2.is_movie_sent( self.files[0]["hash"] )
        moviedb2.MOVIE_DATA[self.files[0]["hash"]]["status"] = "sent"
        assert moviedb2.is_movie_sent( self.files[0]["hash"] )

    def test_can_check_movie_data_to_see_if_movie_found(self):
        moviedb2.load_movie_data( self.movie_data_path )
        self.make_file(self.new_file)
        assert moviedb2.is_new_movie( moviedb2.get_1mb_checksum(self.new_file))
        assert not moviedb2.is_new_movie( self.files[0]["hash"] )

    def test_load_movie_data_sets_empty_dict_if_no_file(self):
        moviedb2.load_movie_data( "some_non_existant_file.json" )
        data = moviedb2.MOVIE_DATA
        assert_equals(type(data).__name__, "dict")

    def test_can_read_movie_data_into_memory(self):
        moviedb2.load_movie_data( self.movie_data_path )
        data = moviedb2.MOVIE_DATA
        assert_equals(len(data), 3)
        assert data[self.files[0]["hash"]]["filename"] == self.files[0]["filename"]
        assert data[self.files[1]["hash"]]["filename"] == self.files[1]["filename"]
        assert data[self.files[2]["hash"]]["filename"] == self.files[2]["filename"]

    def test_can_read_variables_from_config(self):
        assert moviedb2.load_config ( os.path.join("tests", "data", "test-config.yml") )
        config = moviedb2.CONFIG
        assert "PATH" in config and config["PATH"] == "/test path/movies/"
        assert "POST_SERVER_URL" in config and config["POST_SERVER_URL"] == "http://test-url.com"
        assert "FILE_EXTS" in config and len(config["FILE_EXTS"]) == 3 and config["FILE_EXTS"][0] == ".avi"

    def test_send_movie_returns_true_if_successful(self):
        with requests_mock.mock() as m:
            m.post(POST_SERVER_URL, status_code=200)
            assert moviedb2.send_movie_to_server(self.files[0]["filename"], self.files[0]["hash"])[0]

    def test_send_movie_returns_false_if_unsuccessful(self):
        with requests_mock.mock() as m:
            m.post(POST_SERVER_URL, status_code=403)
            assert not moviedb2.send_movie_to_server(self.files[0]["filename"], self.files[0]["hash"])[0]

    def test_get_files_without_id_returns_subset_of_files(self):
        Path(os.path.join(self.test_folder, "blah {1980}.avi")).touch() # this one has an invalid IMDB id + 1 in the setUp = 2
        files = moviedb2.get_files_without_id(moviedb2.get_files(self.test_folder))
        assert_equals(len(files), 2)

    def test_get_files_returns_all_movie_files(self):
        files = moviedb2.get_files(self.test_folder)
        assert len(files) == 3
        for f in self.files:
            assert f["filename"] in files

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

    def add_file_to_data_file(self, filename):
        try:
            with open(self.movie_data_path, 'r') as f:
                data = json.load(f)
        except:
            data = {}
        data[moviedb2.get_1mb_checksum(filename)]= {"filename": filename, "status":"found"}
        with open(self.movie_data_path, 'w') as f:
            json.dump(data, f)

    def make_file(self, filename):
        with open(filename, 'wb') as f:
            f.write(os.urandom(2097152)) #2mb

    def setUp(self):
        self.test_folder = os.path.join("tests", "data" "test_movies")
        self.movie_data_path = os.path.join("tests", "data", "test-movie-data.json")
        self.tmp_movie_data_path = os.path.join("tests", "data", "test-movie-data-modified.json")
        self.new_file = os.path.join(self.test_folder,"filename4.avi")
        moviedb2.load_config ( "config.yml" )
        self.files = [ {"filename": os.path.join(self.test_folder, "test1 {tt1234567}.avi")},
                       {"filename": os.path.join(self.test_folder, "A", "test2 {tt2345678}.mp4")},
                       {"filename": os.path.join(self.test_folder, "B", "test3.mkv")}]
        os.mkdir(self.test_folder)
        os.mkdir(os.path.join(self.test_folder, "A"))
        os.mkdir(os.path.join(self.test_folder, "B"))
        for f in self.files:
            self.make_file(f["filename"])
            self.add_file_to_data_file(f["filename"])
            f["hash"] = moviedb2.get_1mb_checksum(f["filename"])

    def tearDown(self):
        try:
            os.remove(self.movie_data_path)
        except OSError: pass
        try:
            os.remove(self.tmp_movie_data_path)
        except OSError: pass
        if os.path.exists(self.test_folder):
            if os.path.isdir(self.test_folder):
                shutil.rmtree(self.test_folder)
            else:
                os.remove(self.test_folder)
