#!/bin/bash
PROJECT_DIR="$( cd "$(  dirname "${BASH_SOURCE[0]}" )" && cd .. && pwd )"
cd "${PROJECT_DIR}"

echo "**> client tests"
#bash client/run-tests.sh

echo "**> server tests"
#bash server/run-tests.sh

echo "**> integration tests"
mkdir -p "${PROJECT_DIR}/tests/movies-folder"

PID_FOLDER="/tmp/moviedb"
mkdir -p "${PID_FOLDER}"
bash server/run.sh "${PID_FOLDER}"
bash client/run.sh "${PID_FOLDER}"

head -c 2097152 /dev/urandom > "${PROJECT_DIR}/tests/movies-folder/movie1.avi"
head -c 2097152 /dev/urandom > "${PROJECT_DIR}/tests/movies-folder/movie2.avi"
head -c 2097152 /dev/urandom > "${PROJECT_DIR}/tests/movies-folder/movie3.avi"

sleep 11s

nosetests tests/integration-tests.py:IntegrationTestCase

#echo "Client ID ${CLIENT_PID}"
#echo "Server ID ${SERVER_PID}"

echo "**>cleaning up"
# Kill server and client
kill -9 `cat ${PID_FOLDER}/client.pid`
kill -9 `cat ${PID_FOLDER}/server.pid`

rm "${PROJECT_DIR}/client/movie_data.json"
rm -rf "${PROJECT_DIR}/tests/movies-folder"
