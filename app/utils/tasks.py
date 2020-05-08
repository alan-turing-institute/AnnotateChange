# -*- coding: utf-8 -*-

# Author: G.J.J. van den Burg <gvandenburg@turing.ac.uk>
# License: See LICENSE file
# Copyright: 2020 (c) The Alan Turing Institute

"""Utilities for task assignment

"""

import random
import multiprocessing

from flask import current_app

from app.models import Dataset, Task

TASK_LOCK = multiprocessing.Lock()


def generate_user_task(user):
    task = None
    TASK_LOCK.acquire(timeout=10)
    try:
        task = realgenerate_user_task(user)
    finally:
        TASK_LOCK.release()
    return task


def realgenerate_user_task(user):
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

    # don't assign a new task if the user has assigned tasks
    not_done = [t for t in user_tasks if not t.done]
    if len(not_done) > 0:
        return None

    # don't assign a new task if the user has reached maximum
    n_user_tasks = len(user_tasks)
    if n_user_tasks >= max_per_user:
        return None

    # collect datasets that can be potentially assigned to the user
    potential_datasets = []
    for dataset in Dataset.query.filter_by(is_demo=False).all():
        dataset_tasks = Task.query.filter_by(dataset_id=dataset.id).all()

        # check that this dataset needs more annotations
        n_needed = num_per_dataset - len(dataset_tasks)

        # check that this dataset is not already assigned to the user
        task = Task.query.filter_by(
            dataset_id=dataset.id, annotator_id=user.id
        ).first()
        if not task is None:
            continue
        potential_datasets.append((n_needed, dataset))

    # don't assign a dataset if there are no more datasets to annotate (user
    # has done all)
    if len(potential_datasets) == 0:
        return None

    # First try assigning a random dataset that still needs annotations
    dataset = None
    need_annotations = [d for n, d in potential_datasets if n > 0]

    # Weights are set to prioritize datasets that need fewer annotations to
    # reach our goal (num_per_dataset), with a small chance of selecting
    # another dataset.
    weights = [
        (num_per_dataset - n + 0.01) for n, d in potential_datasets if n > 0
    ]
    if need_annotations:
        dataset = random.choices(need_annotations, weights=weights)[0]
    else:
        # if there are no such datasets, then this user is requesting
        # additional annotations after all datasets have our desired coverage
        # of num_per_dataset. Assign a random dataset that has the least excess
        # annotations (thus causing even distribution).
        max_nonpos = max((n for n, d in potential_datasets if n <= 0))
        extra = [d for n, d in potential_datasets if n == max_nonpos]
        if extra:
            dataset = random.choice(extra)

    if dataset is None:
        return None

    task = Task(annotator_id=user.id, dataset_id=dataset.id)
    return task
