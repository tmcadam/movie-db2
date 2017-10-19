#!/bin/bash

# Go to the project directory
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd ${PROJECT_DIR}

# Setup virtualenv, if it doesn't already exist
if [ -d ".env" ]; then
    echo "**> virtualenv exists"
else
    echo "**> creating virtualenv"
    pyvenv-3.5 .env
fi

# Enter virtualenv
echo "**> activating virtual environment"
set +u
source .env/bin/activate > /dev/null
set -u

# Install dependencies
echo "**> installing dependencies"
pip install -U pip-tools > /dev/null
pip install -U setuptools > /dev/null
pip-compile -o requirements.txt requirements.in > /dev/null
pip-compile -o requirements-dev.txt requirements-dev.in > /dev/null
pip-sync requirements.txt requirements-dev.txt > /dev/null

# Run tests
echo "**> running tests"
nosetests

echo "**> build complete"

