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
    TASKS_MAX_PER_USER = 5
    TASKS_NUM_PER_DATASET = 10
