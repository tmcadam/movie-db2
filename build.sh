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
pip-compile -o requirements-dev.txt requirements-dev.in > /dev/null
pip-sync requirements-dev.txt > /dev/null

# Install PhantomJS

mkdir -p ${PROJECT_DIR}/tests/phantomjs/
cd ${PROJECT_DIR}/tests/phantomjs/
if [ ! -d "phantomjs-2.1.1-linux-x86_64" ]; then
    echo "**> installing PhantomJS"
    wget -O download.tar.bz2 https://bitbucket.org/ariya/phantomjs/downloads/phantomjs-2.1.1-linux-x86_64.tar.bz2
    tar -xjvf download.tar.bz2
    rm download.tar.bz2
fi

bash "${PROJECT_DIR}/client/build.sh"
bash "${PROJECT_DIR}/server/build.sh"
