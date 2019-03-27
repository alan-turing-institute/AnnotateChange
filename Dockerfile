FROM python:3.6-alpine

RUN adduser -D annotatechange

WORKDIR /home/annotatechange

# See: https://stackoverflow.com/q/53835198/
ARG YOUR_ENV
ENV YOUR_ENV=${YOUR_ENV} \
	     PYTHONFAULTHANDLER=1 \
	PYTHONUNBUFFERED=1\
	PYTHONHASHSEED=random \
	PIP_NO_CACHE_DIR=off \
	PIP_DIABLE_PIP_VERSION_CHECK=on \
	PIP_DEFAULT_TIMEOUT=100 \
	POETRY_VERSION=0.12.11

RUN pip install "poetry==$POETRY_VERSION"

COPY poetry.lock pyproject.toml /home/annotatechange

RUN poetry config settings.virtualenvs.create false \
	    && poetry install $(test "$YOUR_ENV" == production && echo "--no-dev") \
	    --no-interaction --no-ansi

COPY app app
COPY migrations migrations
COPY annotate_change.py config.py boot.sh ./
RUN chmod +x boot.sh

ENV FLASK_APP annotate_change.py

RUN chown -R annotate_change:annotate_change ./
USER annotate_change

EXPOSE 80
ENTRYPOINT ["./boot.sh"]
