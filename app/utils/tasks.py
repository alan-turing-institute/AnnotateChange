# -*- coding: utf-8 -*-

"""Utilities for task assignment

"""


from flask import current_app

from app.models import User, Dataset, Task


def generate_user_task(user):
    """
    Generate new task for a given user.

    This function assigns tasks to a given user and ensures that:

        1) datasets that are nearly annotated with the desired number of 
        datasets get priority
        2) users never are given more tasks than max_per_user
        3) users never get the same dataset twice

    """
    max_per_user = current_app.config["TASKS_MAX_PER_USER"]
    num_per_dataset = current_app.config["TASKS_NUM_PER_DATASET"]

    user_tasks = Task.query.filter_by(annotator_id=user.id).all()
    user_tasks = [t for t in user_tasks if not t.dataset.is_demo]
    n_user_tasks = len(user_tasks)
    if n_user_tasks >= max_per_user:
        return None

    potential_datasets = []
    for dataset in Dataset.query.filter_by(is_demo=False).all():
        dataset_tasks = Task.query.filter_by(dataset_id=dataset.id).all()

        # check that this dataset needs more annotations
        n_needed = num_per_dataset - len(dataset_tasks)
        if n_needed <= 0:
            continue

        # check that this dataset is not already assigned to the user
        task = Task.query.filter_by(
            dataset_id=dataset.id, annotator_id=user.id
        ).first()
        if not task is None:
            continue
        potential_datasets.append((n_needed, dataset))

    if len(potential_datasets) == 0:
        return None

    # sort datasets so that the ones who need the least are at the front.
    potential_datasets.sort()

    _, dataset = potential_datasets[0]
    task = Task(annotator_id=user.id, dataset_id=dataset.id)
    return task
