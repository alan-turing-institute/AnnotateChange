# -*- coding: utf-8 -*-

from flask import render_template, flash, redirect, url_for
from flask_login import login_required

from app import db
from app.admin import bp
from app.admin.decorators import admin_required
from app.admin.forms import AdminAssignTaskForm
from app.models import User, Dataset, Task


@bp.route("/assign", methods=("GET", "POST"))
@login_required
@admin_required
def assign():
    form = AdminAssignTaskForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash("User does not exist.")
            return redirect(url_for("admin.assign"))
        dataset = Dataset.query.filter_by(name=form.dataset.data).first()
        if dataset is None:
            flash("Dataset does not exist.")
            return redirect(url_for("admin.assign"))

        task = Task.query.filter_by(
            annotator_id=user.id, dataset_id=dataset.id
        )
        if not task is None:
            flash("Task assignment already exists.")
            return redirect(url_for("admin.assign"))

        task = Task(annotator_id=user.id, dataset_id=dataset.id)
        db.session.add(task)
        db.session.commit()
        flash("Task registered successfully.")
    tasks = Task.query.all()
    return render_template(
        "admin/assign.html", title="Assign Task", form=form, tasks=tasks
    )
