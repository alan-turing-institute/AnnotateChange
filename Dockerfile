# Author: G.J.J. van den Burg <gvandenburg@turing.ac.uk>

FROM python:3.7-alpine

RUN apk add gcc musl-dev libffi-dev openssl-dev libxslt-dev build-base

# This Dockerfile is based on:
# https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xix-deployment-on-docker-containers

RUN addgroup --gid 1024 mygroup
RUN adduser --ingroup mygroup -D annotatechange

WORKDIR /home/annotatechange

# See: https://stackoverflow.com/q/53835198/
ARG YOUR_ENV
ENV YOUR_ENV=${YOUR_ENV} \
	PYTHONFAULTHANDLER=1 \
	PYTHONUNBUFFERED=1\
	PYTHONHASHSEED=random \
	PIP_NO_CACHE_DIR=off \
	PIP_DIABLE_PIP_VERSION_CHECK=on \
	PIP_DEFAULT_TIMEOUT=60

COPY requirements.txt /home/annotatechange/
RUN pip install -r requirements.txt

COPY app app
COPY migrations migrations
COPY annotate_change.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP annotate_change.py

RUN mkdir -p /home/annotatechange/instance
VOLUME /home/annotatechange/instance

RUN ls -lh /home/annotatechange/instance

RUN chown -R annotatechange:mygroup /home/annotatechange
USER annotatechange

EXPOSE 7831
ENTRYPOINT ["./boot.sh"]
