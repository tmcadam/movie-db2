#!/bin/bash
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${PROJECT_DIR}"
source .env/bin/activate
export PYTHONPATH=${PYTHONPATH}:${PROJECT_DIR}/moviedb2
export FLASK_APP=moviedb2
export FLASK_DEBUG=true
sudo service mongod restart
nosetests
deactivate
