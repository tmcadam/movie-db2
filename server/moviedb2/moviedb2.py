import json
from flask import Flask, request
from .database_helpers import connect_db

app = Flask(__name__)
app.config.from_object('config.DevelopmentConfig')

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/moviesdb2/api/v1.0/filenames', methods=['POST'])
def get_tasks():
    db = connect_db(app)
    content = request.get_json()
    db.movie_filenames.insert_one(content)
    return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
