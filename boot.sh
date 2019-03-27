#!/bin/sh

# Activate the virtual environment
poetry shell

# Run database migrations
while true; do
	flask db upgrade
	if [[ "$?" == "0" ]]; then
		break;
	fi
	echo "Upgrade command failed, retrying in 5 seconds ..."
	sleep 5
done

exec gunicorn -b :80 --access-logfile - --error-logfile - annotate_change:app
