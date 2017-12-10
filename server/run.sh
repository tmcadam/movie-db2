#!/bin/bash
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${PROJECT_DIR}"
source .env/bin/activate
export PYTHONPATH=${PYTHONPATH}:${PROJECT_DIR}/moviedb2
export FLASK_APP=moviedb2
export FLASK_DEBUG=true

# Start server
sudo service mongod restart
COMMAND="flask run"
nohup $COMMAND &>>"${PROJECT_DIR}/server.log"&
sleep 1s
PID=$(pgrep -n python3.5)
echo "  **>server pid: ${PID}"
echo $PID>"${1}/server.pid"
deactivate
