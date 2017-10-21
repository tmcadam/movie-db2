import os
import re
import urllib3
import yaml
import json

import requests

CONFIG = None
MOVIE_DATA = None

def write_movie_data( filename ):
    with open(filename, 'w') as f:
        json.dump(MOVIE_DATA, f)

def set_movie_sent( filename ):
    global MOVIE_DATA
    MOVIE_DATA[filename]["status"] = "sent"

def add_new_movie( filename ):
    global MOVIE_DATA
    MOVIE_DATA[filename] = {"status": "found"}

def is_movie_sent( filename ):
    return MOVIE_DATA[filename]["status"] == "sent"

def is_new_movie( filename ):
    return filename not in MOVIE_DATA

def load_movie_data ( filename ):
    global MOVIE_DATA
    try:
        with open(filename, 'r') as f:
            MOVIE_DATA = json.load(f)
    except FileNotFoundError as e:
        MOVIE_DATA = dict()

def load_config ( filename ):
    with open(filename, 'r') as f:
        try:
            global CONFIG
            CONFIG = yaml.load(f)
        except yaml.YAMLError as e:
            # write something to logs
            return False
    return True

def send_filename_to_server ( filename ):
    try:
        r = requests.post(CONFIG["POST_SERVER_URL"], json={"file_name": filename})
        if r.status_code == 200:
            return True
        return False
    except (ConnectionRefusedError, requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError) :
        return False

def get_files_without_id( files ):
    return [ f for f in files if not re.search('\{tt\d{7}\}', f) ]

def get_files ( path ):
    return [os.path.join(root, name)
            for root, dirs, files in os.walk(path)
            for name in files
            if os.path.splitext(name)[1] in CONFIG["FILE_EXTS"]]

def check_folder_exists ( path ):
    return os.path.exists(path) and os.path.isdir(path)

def monitor_folder ( path, movie_data_path ):
    folder_stats = {"sent":0, "count":0, "found":0}
    if not check_folder_exists( path ):
        return None
    load_movie_data (movie_data_path)
    files = get_files_without_id( get_files( path ) )
    if files:
        for filename in files:
            folder_stats["count"] += 1
            send = False
            if is_new_movie ( filename ):
                folder_stats["found"] += 1
                add_new_movie ( filename )
                send = True
            elif not is_new_movie ( filename ) and not is_movie_sent ( filename ):
                send = True
            if send and send_filename_to_server( filename ):
                set_movie_sent( filename )
                folder_stats["sent"] += 1
    write_movie_data (movie_data_path)
    return folder_stats
