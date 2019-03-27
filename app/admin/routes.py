# -*- coding: utf-8 -*-

import os
import random

from flask import render_template, flash, redirect, url_for, current_app

from werkzeug.utils import secure_filename

from app import db
from app.admin import bp
from app.admin.datasets import get_name_from_dataset, md5sum
from app.decorators import admin_required
from app.admin.forms import (
    AdminAutoAssignForm,
    AdminManageTaskForm,
    AdminAddDatasetForm,
    AdminManageDatasetsForm,
)
from app.models import User, Dataset, Task, Annotation


@bp.route("/manage/tasks", methods=("GET", "POST"))
@admin_required
def manage_tasks():
    form_auto = AdminAutoAssignForm()

    user_list = [(u.id, u.username) for u in User.query.all()]
    dataset_list = [(d.id, d.name) for d in Dataset.query.all()]

    form_manual = AdminManageTaskForm()
    form_manual.username.choices = user_list
    form_manual.dataset.choices = dataset_list

    if form_auto.validate_on_submit():
        max_per_user = form_auto.max_per_user.data
        num_per_dataset = form_auto.num_per_dataset.data

        available_users = {}
        for user in User.query.all():
            user_tasks = Task.query.filter_by(annotator_id=user.id).all()
            if len(user_tasks) < max_per_user:
                available_users[user] = max_per_user - len(user_tasks)

        if not available_users:
            flash(
                "All users already have at least %i tasks assigned to them."
                % max_per_user,
                "error",
            )
            return redirect(url_for("admin.manage_tasks"))

        datasets_tbd = {}
        for dataset in Dataset.query.all():
            dataset_tasks = Task.query.filter_by(dataset_id=dataset.id).all()
            if len(dataset_tasks) < num_per_dataset:
                datasets_tbd[dataset] = num_per_dataset - len(dataset_tasks)

        if not datasets_tbd:
            flash(
                "All datasets have at least the desired number (%i) of assigned tasks."
                % num_per_dataset,
                "info",
            )
            return redirect(url_for("admin.manage_tasks"))

        datasets = list(datasets_tbd.keys())
        random.shuffle(datasets)
        for dataset in datasets:
            available = [u for u, v in available_users.items() if v > 0]
            tbd = min(len(available), datasets_tbd[dataset])
            selected_users = random.sample(available, tbd)
            for user in selected_users:
                task = Task(annotator_id=user.id, dataset_id=dataset.id)
                db.session.add(task)
                db.session.commit()
                available_users[user] -= 1
                datasets_tbd[dataset] -= 1
        flash("Automatic task assignment successful.", "success")

    elif form_manual.validate_on_submit():
        user = User.query.filter_by(id=form_manual.username.data).first()
        if user is None:
            flash("User does not exist.", "error")
            return redirect(url_for("admin.manage_tasks"))
        dataset = Dataset.query.filter_by(id=form_manual.dataset.data).first()
        if dataset is None:
            flash("Dataset does not exist.", "error")
            return redirect(url_for("admin.manage_tasks"))

        action = None
        if form_manual.assign.data:
            action = "assign"
        elif form_manual.delete.data:
            action = "delete"
        else:
            flash(
                "Internal error: no button is true but form_manual was submitted.",
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

    tasks = (
        Task.query.join(User, Task.user)
        .join(Dataset, Task.dataset)
        .order_by(Dataset.name, User.username)
        .all()
    )
    return render_template(
        "admin/manage.html",
        title="Assign Task",
        form_auto=form_auto,
        form_manual=form_manual,
        tasks=tasks,
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

        dataset_dir = os.path.join(
            current_app.instance_path, current_app.config["DATASET_DIR"]
        )
        filename = os.path.join(dataset_dir, dataset.name + ".json")
        if not os.path.exists(filename):
            flash("Internal error: dataset file doesn't exist!", "error")
            return redirect(url_for("admin.manage_datasets"))

        tasks = Task.query.filter_by(dataset_id=dataset.id).all()
        for task in tasks:
            for ann in Annotation.query.filter_by(task_id=task.id).all():
                db.session.delete(ann)
            db.session.delete(task)
        db.session.delete(dataset)
        db.session.commit()
        os.unlink(filename)
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
