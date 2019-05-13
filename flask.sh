#!/bin/bash

export $(grep -v '^#' .env.development | xargs -d '\n')

echo "FLASK_APP = ${FLASK_APP}"
echo "FLASK_ENV = ${FLASK_ENV}"
echo "Running: flask $*"

poetry run flask "$@"
