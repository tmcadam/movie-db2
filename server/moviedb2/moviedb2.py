import json
from flask import Flask, request

app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/moviesdb2/api/v1.0/filenames', methods=['POST'])
def get_tasks():
    print (request.is_json)
    content = request.get_json()
    print (content)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
