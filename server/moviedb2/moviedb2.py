import json
from flask import Flask, request, render_template
from .database_helpers import connect_db, insert_timestamped_doc

app = Flask(__name__)
app.config.from_object('config.TestingConfig')

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/moviesdb2/api/v1.0/filenames', methods=['POST'])
def post_movies():
    db = connect_db(app)
    content = request.get_json()
    content["status"] = "new"
    if insert_timestamped_doc(db.movie_names, content):
        # run some new movie process
        return json.dumps({'success':True}), 200, {'ContentType':'application/json'}
    return json.dumps({'success': False, "code": 1, "message": "Duplicate file"}), 400, {'ContentType':'application/json'}

@app.route('/moviesdb2/filenames', methods=['GET'])
def get_movies():
    db = connect_db(app)
    movies = db.movie_names.find()
    return render_template('movies.html', movies=movies)
