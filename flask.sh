#!/bin/bash

# Author: G.J.J. van den Burg <gvandenburg@turing.ac.uk>

export $(grep -v '^#' .env.development | xargs -d '\n')

echo "FLASK_APP = ${FLASK_APP}"
echo "FLASK_ENV = ${FLASK_ENV}"
echo "Running: flask $*"

poetry run flask "$@"
