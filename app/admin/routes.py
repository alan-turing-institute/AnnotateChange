# -*- coding: utf-8 -*-

import os

from flask import render_template, flash, redirect, url_for, current_app

from werkzeug.utils import secure_filename

from app import db
from app.admin import bp
from app.admin.datasets import get_name_from_dataset, md5sum
from app.admin.decorators import admin_required
from app.admin.forms import AdminAssignTaskForm, AdminAddDatasetForm
from app.models import User, Dataset, Task


@bp.route("/assign", methods=("GET", "POST"))
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


@bp.route("/add", methods=("GET", "POST"))
@admin_required
def add_dataset():
    tmp_dir = os.path.join(
        current_app.instance_path, current_app.config["TEMP_DIR"]
    )
    dataset_dir = os.path.join(
        current_app.instance_path, current_app.config["DATASET_DIR"]
    )
    form = AdminAddDatasetForm()
    if form.validate_on_submit():
        temp_filename = os.path.join(
            tmp_dir, secure_filename(form.file_.data.filename)
        )
        if not os.path.exists(temp_filename):
            flash("Internal error: temporary dataset disappeared.")
            return redirect(url_for("admin.add_dataset"))
        name = get_name_from_dataset(temp_filename)
        target_filename = os.path.join(dataset_dir, name + ".json")
        if os.path.exists(target_filename):
            flash("Internal error: file already exists!")
            return redirect(url_for("admin.add_dataset"))
        os.rename(temp_filename, target_filename)
        if not os.path.exists(target_filename):
            flash("Internal error: file moving failed")
            return redirect(url_for("admin.add_dataset"))

        dataset = Dataset(name=name, md5sum=md5sum(target_filename))
        db.session.add(dataset)
        db.session.commit()
        flash("Dataset %r added successfully.", name)
        return redirect(url_for("admin.add_dataset"))
    return render_template("admin/add.html", title="Add Dataset", form=form)


@bp.route("/", methods=("GET",))
@admin_required
def index():
    return render_template("admin/index.html", title="Admin Home")
