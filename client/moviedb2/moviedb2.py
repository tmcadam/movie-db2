import requests

def hello_world():
    r = requests.get('https://www.google.com.au')
    return r.status_code
