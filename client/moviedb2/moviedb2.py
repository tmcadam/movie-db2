import os
import re
import urllib3
import yaml
import json
import hashlib

import requests

CONFIG = None
MOVIE_DATA = None

def get_1mb_checksum( filename ):
    with open(filename, 'rb') as f:
        md5 = hashlib.md5(f.read(1048576))
    return md5.hexdigest()

def write_movie_data( filename ):
    with open(filename, 'w') as f:
        json.dump(MOVIE_DATA, f)

def set_movie_sent( hash ):
    global MOVIE_DATA
    MOVIE_DATA[hash]["status"] = "sent"

def add_new_movie( filename, hash ):
    global MOVIE_DATA
    MOVIE_DATA[hash] = {"filename": filename, "status": "found"}

def is_movie_sent( hash ):
    return not is_new_movie(hash) and MOVIE_DATA[hash]["status"] == "sent"

def is_new_movie( hash ):
    return hash not in MOVIE_DATA

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

def send_movie_to_server ( filename, hash ):
    try:
        r = requests.post(CONFIG["POST_SERVER_URL"], json={"hash": hash, "filename": filename})
        if r.status_code == 200:
            return (True, None)
        elif r.status_code == 400:
            content = r.json()
            return (False, content["code"])
        return (False, 0)
    except (ConnectionRefusedError, requests.exceptions.ConnectionError, urllib3.exceptions.MaxRetryError, urllib3.exceptions.NewConnectionError) :
        return (False, 0)

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
    if not check_folder_exists( path ):
        return None
    load_movie_data (movie_data_path)
    files = get_files_without_id( get_files( path ) )
    folder_stats = {"sent":0, "found":0, "count":len(files)}
    for filename in files:
        hash = get_1mb_checksum( filename )
        if not is_movie_sent ( hash ):
            if is_new_movie ( hash ):
                folder_stats["found"] += 1
                add_new_movie ( filename, hash )
            r = send_movie_to_server( filename, hash )
            if r[0]:
                set_movie_sent( hash )
                folder_stats["sent"] += 1
            else:
                if r[1] == 1:
                    set_movie_sent( hash )
    write_movie_data (movie_data_path)
    return folder_stats
