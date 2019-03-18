
import datetime

from flask_login import UserMixin

from werkzeug.security import generate_password_hash, check_password_hash

from app import db
from app import login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    last_active = db.Column(
        db.DateTime(), nullable=False, default=datetime.datetime.utcnow
    )

    def __repr__(self):
        return "<User %r>" % self.username

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Dataset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), unique=True, nullable=False)
    created = db.Column(
        db.DateTime, nullable=False, default=datetime.datetime.utcnow
    )
    md5sum = db.Column(db.String(32), unique=True, nullable=False)

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
    time_start = db.Column(db.Integer)
    time_end = db.Column(db.Integer)

    task = db.relation("Task")
    task_id = db.Column(db.Integer, db.ForeignKey("task.id"))

    def __repr__(self):
        return "<Annotation %r>" % self.id


@login.user_loader
def load_user(_id):
    return User.query.get(int(_id))
