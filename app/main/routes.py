# -*- coding: utf-8 -*-

from flask import render_template
from flask_login import current_user

from app.main import bp
from app.models import Task


@bp.route("/")
@bp.route("/index")
def index():
    if current_user.is_authenticated:
        user_id = current_user.id
        tasks = Task.query.filter_by(annotator_id=user_id).all()
        tasks_done = [t for t in tasks if t.done]
        tasks_todo = [t for t in tasks if not t.done]
        return render_template("index.html", title="Home", 
                tasks_done=tasks_done, tasks_todo=tasks_todo)
    return render_template("index.html", title="Home")
