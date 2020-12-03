#!/bin/sh
#
# Script to run the AnnotateChange application.
#
# First tries to perform all database migrations, then launches the app 
# through gunicorn. The script assumes that all dependencies are available in 
# the environment.
#
# Author: G.J.J. van den Burg <gvandenburg@turing.ac.uk>

# Run database migrations
while true; do
	flask db upgrade
	if [[ "$?" == "0" ]]; then
		break;
	fi
	echo "Upgrade command failed, retrying in 5 seconds ..."
	sleep 5
done

exec gunicorn -b :7831 --preload --access-logfile - --error-logfile - annotate_change:app
