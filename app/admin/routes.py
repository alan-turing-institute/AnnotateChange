# -*- coding: utf-8 -*-

import os

from flask import render_template, flash, redirect, url_for, current_app

from werkzeug.utils import secure_filename

from app import db
from app.admin import bp
from app.admin.datasets import get_name_from_dataset, md5sum
from app.decorators import admin_required
from app.admin.forms import (
    AdminManageTaskForm,
    AdminAddDatasetForm,
    AdminManageDatasetsForm,
)
from app.models import User, Dataset, Task, Annotation


@bp.route("/manage/tasks", methods=("GET", "POST"))
@admin_required
def manage_tasks():
    user_list = [(u.id, u.username) for u in User.query.all()]
    dataset_list = [(d.id, d.name) for d in Dataset.query.all()]

    form = AdminManageTaskForm()
    form.username.choices = user_list
    form.dataset.choices = dataset_list

    if form.validate_on_submit():
        user = User.query.filter_by(id=form.username.data).first()
        if user is None:
            flash("User does not exist.", "error")
            return redirect(url_for("admin.manage_tasks"))
        dataset = Dataset.query.filter_by(id=form.dataset.data).first()
        if dataset is None:
            flash("Dataset does not exist.", "error")
            return redirect(url_for("admin.manage_tasks"))

        action = None
        if form.assign.data:
            action = "assign"
        elif form.delete.data:
            action = "delete"
        else:
            flash(
                "Internal error: no button is true but form was submitted.",
                "error",
            )
            return redirect(url_for("admin.manage_tasks"))

        task = Task.query.filter_by(
            annotator_id=user.id, dataset_id=dataset.id
        ).first()
        if task is None:
            if action == "delete":
                flash("Can't delete a task that doesn't exist.", "error")
                return redirect(url_for("admin.manage_tasks"))
            else:
                task = Task(annotator_id=user.id, dataset_id=dataset.id)
                db.session.add(task)
                db.session.commit()
                flash("Task registered successfully.", "success")
        else:
            if action == "assign":
                flash("Task assignment already exists.", "error")
                return redirect(url_for("admin.manage_tasks"))
            else:
                # delete annotations too
                for ann in Annotation.query.filter_by(task_id=task.id).all():
                    db.session.delete(ann)
                db.session.delete(task)
                db.session.commit()
                flash("Task deleted successfully.", "success")

    tasks = Task.query.join(User, Task.user).order_by(User.username).all()
    return render_template(
        "admin/manage.html", title="Assign Task", form=form, tasks=tasks
    )


@bp.route("/manage/users", methods=("GET", "POST"))
@admin_required
def manage_users():
    users = User.query.all()
    return render_template(
        "admin/manage_users.html", title="Manage Users", users=users
    )


@bp.route("/manage/datasets", methods=("GET", "POST"))
@admin_required
def manage_datasets():
    dataset_list = [(d.id, d.name) for d in Dataset.query.all()]

    form = AdminManageDatasetsForm()
    form.dataset.choices = dataset_list

    if form.validate_on_submit():
        dataset = Dataset.query.filter_by(id=form.dataset.data).first()
        if dataset is None:
            flash("Dataset doesn't exist.", "error")
            return redirect(url_for("admin.manage_datasets"))

        tasks = Task.query.filter_by(dataset_id=dataset.id).all()
        for task in tasks:
            for ann in Annotation.query.filter_by(task_id=task.id).all():
                db.session.delete(ann)
            db.session.delete(task)
        db.session.delete(dataset)
        db.session.commit()
        flash("Dataset deleted successfully.", "success")

    overview = []
    for dataset in Dataset.query.all():
        tasks = Task.query.filter_by(dataset_id=dataset.id).all()
        n_complete = len([t for t in tasks if t.done])
        perc = n_complete / len(tasks) * 100
        entry = {
            "id": dataset.id,
            "name": dataset.name,
            "assigned": len(tasks),
            "completed": n_complete,
            "percentage": perc,
        }
        overview.append(entry)
    return render_template(
        "admin/manage_datasets.html",
        title="Manage Datasets",
        overview=overview,
        form=form,
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
            flash("Internal error: temporary dataset disappeared.", "error")
            return redirect(url_for("admin.add_dataset"))
        name = get_name_from_dataset(temp_filename)
        target_filename = os.path.join(dataset_dir, name + ".json")
        if os.path.exists(target_filename):
            flash("Internal error: file already exists!", "error")
            return redirect(url_for("admin.add_dataset"))
        os.rename(temp_filename, target_filename)
        if not os.path.exists(target_filename):
            flash("Internal error: file moving failed", "error")
            return redirect(url_for("admin.add_dataset"))

        dataset = Dataset(name=name, md5sum=md5sum(target_filename))
        db.session.add(dataset)
        db.session.commit()
        flash("Dataset %r added successfully." % name, "success")
        return redirect(url_for("admin.add_dataset"))
    return render_template("admin/add.html", title="Add Dataset", form=form)


@bp.route("/annotations", methods=("GET",))
@admin_required
def view_annotations():
    annotations = (
        Annotation.query.join(Task, Annotation.task)
        .join(User, Task.user)
        .join(Dataset, Task.dataset)
        .order_by(Dataset.name, User.username, Annotation.cp_index)
        .all()
    )
    return render_template(
        "admin/annotations.html",
        title="View Annotations",
        annotations=annotations,
    )


@bp.route("/", methods=("GET",))
@admin_required
def index():
    return render_template("admin/index.html", title="Admin Home")
