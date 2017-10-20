import requests
import os
import re

POST_SERVER_URL = "http://someurl.com/api/v1/file_names"

def send_filename_to_server( filename ):
    r = requests.post(POST_SERVER_URL, json={"file_name": filename})
    if r.status_code == 200:
        return True
    return False

def get_files_without_id( files ):
    return [ f for f in files if not re.search('\{tt\d{7}\}', f) ]

def get_files( path ):
    FILE_EXTS = [".avi", ".mp4", ".mkv"]
    return [os.path.join(root, name)
            for root, dirs, files in os.walk(path)
            for name in files
            if os.path.splitext(name)[1] in FILE_EXTS]

def check_folder_exists( path ):
    return os.path.exists(path) and os.path.isdir(path)
