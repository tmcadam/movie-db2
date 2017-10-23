#!/bin/bash
PROJECT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "${PROJECT_DIR}"
source .env/bin/activate
nosetests
deactivate
