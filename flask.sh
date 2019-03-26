#!/bin/bash

export FLASK_APP=annotate_change_v2.py
export FLASK_ENV=development

echo "FLASK_APP = ${FLASK_APP}"
echo "FLASK_ENV = ${FLASK_ENV}"
echo "Running: flask $*"

poetry run flask "$@"
