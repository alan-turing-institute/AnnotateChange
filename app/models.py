# -*- coding: utf-8 -*-

import datetime
import jwt
import time

from flask import current_app
from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(256), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_active = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )
    is_admin = db.Column(db.Boolean(), default=False)

    # after email is confirmed:
    is_confirmed = db.Column(db.Boolean(), default=False)

    # after all demo tasks completed:
    is_introduced = db.Column(db.Boolean(), default=False)

    # checkboxes during registration
    read_toc = db.Column(db.Boolean(), default=False)
    wants_credit = db.Column(db.Boolean(), default=False)
    wants_updates = db.Column(db.Boolean(), default=False)

    # full name
    fullname = db.Column(db.String(256), unique=False, nullable=True)

    def __repr__(self):
        return "<User %r>" % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {"reset_password": self.id, "exp": time.time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_reset_password_token(token):
        try:
            _id = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["reset_password"]
        except:
            return None
        return User.query.get(_id)

    def get_email_confirmation_token(self, expires_in=3600):
        return jwt.encode(
            {"email": self.email, "exp": time.time() + expires_in},
            current_app.config["SECRET_KEY"],
            algorithm="HS256",
        ).decode("utf-8")

    @staticmethod
    def verify_email_confirmation_token(token):
        try:
            _email = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )["email"]
        except:
            return None
        return User.query.filter_by(email=_email).first()


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    md5sum = db.Column(db.String(32), unique=True, nullable=False)

    # Whether or not dataset is a demo dataset.
    is_demo = db.Column(db.Boolean(), default=True)

    def __repr__(self):
        return "<Dataset %r>" % self.name


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    annotator_id = db.Column(db.Integer, nullable=False)
    dataset_id = db.Column(db.Integer, nullable=False)
    done = db.Column(db.Boolean, nullable=False, default=False)
    annotated_on = db.Column(db.DateTime, nullable=True)

    user = db.relation("User")
    annotator_id = db.Column(db.Integer, db.ForeignKey("user.id"))

    dataset = db.relation("Dataset")
    dataset_id = db.Column(db.Integer, db.ForeignKey("dataset.id"))

    def __repr__(self):
        return "<Task (%r, %r)>" % (self.annotator_id, self.dataset_id)


class Annotation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    cp_index = db.Column(db.Integer)

    task = db.relation("Task")
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"))

    def __repr__(self):
        return "<Annotation %r>" % self.id


@login.user_loader
def load_user(_id):
    return User.query.get(int(_id))
