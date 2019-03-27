#!/bin/sh

# Activate the virtual environment
poetry shell

# Run database migrations
flask db upgrade

exec gunicorn -b :5000 --access-logfile - --error-logfile - annotate_change:app

