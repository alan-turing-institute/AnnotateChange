# -*- coding: utf-8 -*-

from flask import render_template, flash, url_for, redirect
from flask_login import current_user, login_required

from app.main import bp
from app.models import Task
from app.main.datasets import load_data_for_chart


@bp.route("/")
@bp.route("/index")
def index():
    if current_user.is_authenticated:
        user_id = current_user.id
        tasks = Task.query.filter_by(annotator_id=user_id).all()
        tasks_done = [t for t in tasks if t.done]
        tasks_todo = [t for t in tasks if not t.done]
        return render_template(
            "index.html",
            title="Home",
            tasks_done=tasks_done,
            tasks_todo=tasks_todo,
        )
    return render_template("index.html", title="Home")


@bp.route("/annotate/<int:task_id>", methods=("GET", "POST"))
@login_required
def task(task_id):
    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        flash("No task with id %r has been assigned to you." % task_id)
        return redirect(url_for("main.index"))
    data = load_data_for_chart(task.dataset.name)
    return render_template("annotate/index.html", title="Annotate %s" % 
            task.dataset.name, task=task, data=data)
