#!/bin/bash
PROJECT_DIR="$( cd "$(  dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
cd "${PROJECT_DIR}"

echo "**> client tests"
bash client/run-tests.sh

echo "**> server tests"
bash server/run-tests.sh

echo "**> integration tests"
sudo service mongod restart
mkdir -p "${PROJECT_DIR}/tests/movies-folder"

PID_FOLDER="/tmp/moviedb"
mkdir -p "${PID_FOLDER}"

# double check we killed them last time
kill -9 `cat ${PID_FOLDER}/client.pid`> /dev/null 2>&1
kill -9 `cat ${PID_FOLDER}/server.pid`> /dev/null 2>&1

bash server/run.sh "${PID_FOLDER}"
bash client/run.sh "${PID_FOLDER}"

# enter virtualenv
source .env/bin/activate
# clean the test database
python tests/test-helpers.py
# create some test movies
head -c 2097152 /dev/urandom > "${PROJECT_DIR}/tests/movies-folder/movie1.avi"
head -c 2097152 /dev/urandom > "${PROJECT_DIR}/tests/movies-folder/movie2.avi"
head -c 2097152 /dev/urandom > "${PROJECT_DIR}/tests/movies-folder/movie3.avi"

# give the watcher a chance to watch (could make shorter for testing)
sleep 11s

# flash open Firefox at the right page
nohup firefox http://localhost:5000/moviesdb2/filenames &>/dev/null& sleep 1s
PID=$(pgrep -n firefox) && echo "  **>firefox pid: ${PID}" && sleep 4s

# run python tests
nosetests tests/integration-tests.py:IntegrationTestCase

# Kill server and client
echo "**>cleaning up"
kill -9 $PID
kill -9 `cat ${PID_FOLDER}/client.pid`
kill -9 `cat ${PID_FOLDER}/server.pid`

# Some additional cleanup
rm "${PROJECT_DIR}/client/movie_data.json"
rm -rf "${PROJECT_DIR}/tests/movies-folder"
