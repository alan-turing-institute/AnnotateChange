# -*- coding: utf-8 -*-

__version__ = "0.4.0"

import logging
import os

from logging.handlers import SMTPHandler, RotatingFileHandler

from flask import Flask
from flask_bootstrap import Bootstrap, WebCDN
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
login.login_view = "auth.login"
mail = Mail()
bootstrap = Bootstrap()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Set the app version in the config (we use it in templates)
    app.config["APP_VERSION"] = __version__

    # Initialize all extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    bootstrap.init_app(app)

    # Register CDNs
    app.extensions["bootstrap"]["cdns"]["bootstrap"] = WebCDN(
        "/static/resources/bootstrap/"
    )
    app.extensions["bootstrap"]["cdns"]["jquery"] = WebCDN(
        "/static/resources/jquery/"
    )
    app.extensions["bootstrap"]["cdns"]["datatables"] = WebCDN(
        "/static/resources/datatables/"
    )
    app.extensions["bootstrap"]["cdns"]["d3"] = WebCDN("/static/resources/d3/")

    # Initialize the instance directory and necessary subdirectories
    os.makedirs(app.instance_path, exist_ok=True)
    os.makedirs(
        os.path.join(app.instance_path, app.config["TEMP_DIR"]), exist_ok=True
    )
    os.makedirs(
        os.path.join(app.instance_path, app.config["DATASET_DIR"]),
        exist_ok=True,
    )

    # Register all the blueprints
    from app.errors import bp as errors_bp

    app.register_blueprint(errors_bp)

    from app.auth import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main import bp as main_bp

    app.register_blueprint(main_bp)

    from app.admin import bp as admin_bp

    app.register_blueprint(admin_bp)

    # Register the auto_logout function
    from app.auth.routes import auto_logout

    app.before_request(auto_logout)

    if not app.debug:
        if app.config["MAIL_SERVER"]:
            auth = None
            if app.config["MAIL_USERNAME"] or app.config["MAIL_PASSWORD"]:
                auth = (
                    app.config["MAIL_USERNAME"],
                    app.config["MAIL_PASSWORD"],
                )
            secure = None
            if app.config["MAIL_USE_TLS"]:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config["MAIL_SERVER"], app.config["MAIL_PORT"]),
                fromaddr="no-reply@" + app.config["MAIL_SERVER"],
                toaddrs=app.config["ADMINS"],
                subject="AnnotateChange Failure",
                credentials=auth,
                secure=secure,
            )
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists("logs"):
            os.mkdir("logs")
        file_handler = RotatingFileHandler(
            "logs/annotatechange.log", maxBytes=10240, backupCount=10
        )
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]"
            )
        )
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info("AnnotateChange startup")

    return app


from app import models
