#!/bin/bash
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${PROJECT_DIR}"
source .env/bin/activate

# Start client
COMMAND="python -u moviedb2/run.py"
nohup $COMMAND &>>"${PROJECT_DIR}/client.log"&
sleep 1s
PID=$(pgrep -n python)
echo "  **>client pid: ${PID}"
echo $PID>"${1}/client.pid"
deactivate
