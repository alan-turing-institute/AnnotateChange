# -*- coding: utf-8 -*-

"""Utilities for task assignment

"""

import random

from flask import current_app

from app.models import User, Dataset, Task


def generate_auto_assign_tasks(max_per_user, num_per_dataset):
    """Automatically generate random tasks

    This function generates random tasks for the users based on the desired 
    number of tasks per dataset and the maximum number of tasks per user. The 
    return value is a tuple (Task, error) where Task is None if an error 
    occurred.
    """

    # create a dictionary of user/num available tasks
    available_users = {}
    for user in User.query.all():
        user_tasks = Task.query.filter_by(annotator_id=user.id).all()
        if len(user_tasks) < max_per_user:
            available_users[user] = max_per_user - len(user_tasks)

    if not available_users:
        error = (
            "All users already have at least %i tasks assigned to them."
            % max_per_user
        )
        yield (None, error)

    # create a dictionary of dataset/num tasks desired
    datasets_tbd = {}
    for dataset in Dataset.query.all():
        dataset_tasks = Task.query.filter_by(dataset_id=dataset.id).all()
        if len(dataset_tasks) < num_per_dataset:
            datasets_tbd[dataset] = num_per_dataset - len(dataset_tasks)

    if not datasets_tbd:
        error = (
            "All datasets already have at least the desired number (%i) of tasks."
            % num_per_dataset
        )
        yield (None, error)

    # shuffle the dataset list
    datasets = list(datasets_tbd.keys())
    random.shuffle(datasets)
    for dataset in datasets:
        available = [u for u, v in available_users.items() if v > 0]
        tbd = min(len(available), datasets_tbd[dataset])

        # select a random set of users
        selected_users = random.sample(available, tbd)
        for user in selected_users:
            task = Task(annotator_id=user.id, dataset_id=dataset.id)
            yield (task, None)
            available_users[user] -= 1
            datasets_tbd[dataset] -= 1

    if any((datasets_tbd[d] > 0 for d in datasets)):
        yield (
            None,
            "Insufficient users available for the desired number of tasks per dataset.",
        )


def create_initial_user_tasks(user, max_per_user=None, num_per_dataset=None):
    """Generate initial tasks for a given user
    """
    if max_per_user is None:
        max_per_user = current_app.config["TASKS_MAX_PER_USER"]
    if num_per_dataset is None:
        num_per_dataset = current_app.config["TASKS_NUM_PER_DATASET"]

    user_tasks = Task.query.filter_by(annotator_id=user.id).all()
    if len(user_tasks) >= max_per_user:
        yield None
    available_user = max_per_user - len(user_tasks)

    datasets_tbd = {}
    for dataset in Dataset.query.all():
        dataset_tasks = Task.query.filter_by(dataset_id=dataset.id).all()
        if len(dataset_tasks) < num_per_dataset:
            datasets_tbd[dataset] = num_per_dataset - len(dataset_tasks)
    if not datasets_tbd:
        yield None

    # shuffle the dataset list
    datasets = list(datasets_tbd.keys())
    random.shuffle(datasets)
    for dataset in datasets:
        task = Task(annotator_id=user.id, dataset_id=dataset.id)
        yield task
        available_user -= 1
        datasets_tbd[dataset] -= 1
        if available_user == 0:
            break
