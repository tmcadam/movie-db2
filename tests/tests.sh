#!/bin/bash
PROJECT_DIR="$( cd "$(  dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
cd "${PROJECT_DIR}"

# export PhantomJS bin path (could already be installed on Travis)
PATH=${PATH}:${PROJECT_DIR}/tests/phantomjs/phantomjs-2.1.1-linux-x86_64/bin

echo "**> client tests"
bash client/run-tests.sh

echo "**> server tests"
bash server/run-tests.sh

echo "**> integration tests"
# create a tmp folder to store process ids
PID_FOLDER="/tmp/moviedb"
mkdir -p "${PID_FOLDER}"

# double check we killed them last time
kill -9 `cat ${PID_FOLDER}/client.pid`> /dev/null 2>&1
kill -9 `cat ${PID_FOLDER}/server.pid`> /dev/null 2>&1

# start server
sudo service mongod restart
bash server/run.sh "${PID_FOLDER}"
# start client
bash client/run.sh "${PID_FOLDER}"

# enter virtualenv
source .env/bin/activate
mkdir -p "${PROJECT_DIR}/tests/movies-folder"

# run python tests
nosetests tests/integration-tests.py:IntegrationTestCase
nosetests tests/integration-tests.py:BrowserTestCase

# Kill server and client and clean up
echo "**>cleaning up"
# kill -9 $PID
kill -9 `cat ${PID_FOLDER}/client.pid`
kill -9 `cat ${PID_FOLDER}/server.pid`
rm "${PROJECT_DIR}/client/movie_data.json"
