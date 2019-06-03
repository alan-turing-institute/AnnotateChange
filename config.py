# -*- coding: utf-8 -*-

"""Configuration for the AnnotateChange app

Almost all configuration options are expected to be supplied through 
environment variables.
"""

import os

BASEDIR = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"

    DB_TYPE = os.environ.get("DB_TYPE") or "sqlite3"
    if DB_TYPE == "mysql":
        SQLALCHEMY_DATABASE_URI = "mysql+pymysql://{username}:{password}@{host}:{port}/{database}".format(
            username=os.environ.get("AC_MYSQL_USER"),
            password=os.environ.get("AC_MYSQL_PASSWORD"),
            host=os.environ.get("AC_MYSQL_HOST"),
            port=os.environ.get("AC_MYSQL_PORT"),
            database=os.environ.get("AC_MYSQL_DATABASE"),
        )
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///{filepath}".format(
            filepath=os.path.join(
                BASEDIR, os.environ.get("SQL3_FILENAME") or "app.db"
            )
        )

    SQLALCHEMY_TRACK_MODIFICATIONS = False

    MAIL_SERVER = os.environ.get("MAIL_SERVER")
    MAIL_PORT = int(os.environ.get("MAIL_PORT") or 25)
    MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS") is not None
    MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")
    ADMINS = [
        x.strip()
        for x in os.environ.get("ADMIN_EMAILS").split(";")
        if x.strip()
    ]

    # these should be used relative to the instance path
    DATASET_DIR = "datasets"
    TEMP_DIR = "tmp"

    # task distribution settings
    TASKS_MAX_PER_USER =int(os.environ.get("TASKS_MAX_PER_USER")) or 5
    TASKS_NUM_PER_DATASET = int(os.environ.get("TASKS_NUM_PER_DATASET")) or 10

    # user emails allowed
    USER_EMAIL_DOMAINS = os.environ.get("USER_EMAIL_DOMAINS") or ""
    USER_EMAIL_DOMAINS = [
        x.strip() for x in USER_EMAIL_DOMAINS.split(";") if x.strip()
    ]
    USER_EMAIL_DOMAINS = (
        None if not USER_EMAIL_DOMAINS else USER_EMAIL_DOMAINS
    )
    USER_EMAILS = os.environ.get("USER_EMAILS") or ""
    USER_EMAILS = [x.strip() for x in USER_EMAILS.split(";") if x.strip()]
    USER_EMAILS = None if not USER_EMAILS else USER_EMAILS
