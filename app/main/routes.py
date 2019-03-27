# -*- coding: utf-8 -*-

import datetime

from flask import render_template, flash, url_for, redirect, request
from flask_login import current_user

from app import db
from app.decorators import login_required
from app.main import bp
from app.models import Annotation, Task
from app.main.datasets import load_data_for_chart

RUBRIC = """
<i>Please mark all the points in the time series where an abrupt change in
 the behaviour of the series occurs.</i>
<br>
<br>
If there are no such points, please click the "no changepoints" button.
<br>
When you're ready, please click the submit button.
<br>
<b>Note:</b> You can zoom and pan the graph if needed.
<br>
Thank you!
"""


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
    if request.method == "POST":
        # record post time
        now = datetime.datetime.utcnow()

        # get the json from the client
        annotation = request.get_json()
        if annotation["task"] != task_id:
            flash("Internal error: task id doesn't match.", "error")
            return redirect(url_for(task_id=task_id))

        task = Task.query.filter_by(id=task_id).first()

        # remove all previous annotations for this task
        for ann in Annotation.query.filter_by(task_id=task_id).all():
            db.session.delete(ann)
        task.done = False
        task.annotated_on = None
        db.session.commit()

        # record the annotation
        if annotation["changepoints"] is None:
            ann = Annotation(cp_index=None, task_id=task_id)
            db.session.add(ann)
            db.session.commit()
        else:
            for cp in annotation["changepoints"]:
                ann = Annotation(cp_index=cp["x"], task_id=task_id)
                db.session.add(ann)
                db.session.commit()

        # mark the task as done
        task.done = True
        task.annotated_on = now
        db.session.commit()

        flash("Your annotation has been recorded, thank you!", "success")
        return url_for("main.index")

    task = Task.query.filter_by(id=task_id).first()
    if task is None:
        flash("No task with id %r exists." % task_id, "error")
        return redirect(url_for("main.index"))
    if not task.annotator_id == current_user.id:
        flash(
            "No task with id %r has been assigned to you." % task_id, "error"
        )
        return redirect(url_for("main.index"))
    if task.done:
        flash("It's not possible to edit annotations at the moment.")
        return redirect(url_for("main.index"))
    data = load_data_for_chart(task.dataset.name)
    return render_template(
        "annotate/index.html",
        title="Annotate %s" % task.dataset.name,
        task=task,
        data=data,
        rubric=RUBRIC,
    )
