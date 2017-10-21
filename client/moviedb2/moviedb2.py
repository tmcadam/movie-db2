import os
import re
import urllib3
import yaml

import requests

CONFIG = None

def load_config ( filename ):
    with open(filename, 'r') as f:
        try:
            global CONFIG
            CONFIG = yaml.load(f)
        except yaml.YAMLError as exc:
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

def monitor_folder ( path ):
    status = 0
    if not check_folder_exists( path ):
        return 0
    files = get_files_without_id( get_files( path ) )
    if files:
        for filename in files:
            if send_filename_to_server(filename):
                status += 1
    return status
