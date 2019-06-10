# -*- coding: utf-8 -*-

"""
Dataset handling

The dataset model is defined in the adjacent 'dataset_schema.json' file, which 
is a JSONSchema schema definition. It can be easily edited at 
www.jsonschema.net or yapi.demo.qunar.com/editor/

Missing values must be denoted by 'NaN' (this is understood by the JSON 
decoder).

Author: Gertjan van den Burg

"""

import hashlib
import json
import jsonschema
import logging
import os

from flask import current_app

LOGGER = logging.getLogger(__file__)


def load_schema():
    pth = os.path.abspath(__file__)
    basedir = os.path.dirname(pth)
    schema_file = os.path.join(basedir, "dataset_schema.json")
    if not os.path.exists(schema_file):
        raise FileNotFoundError(schema_file)
    with open(schema_file, "rb") as fp:
        schema = json.load(fp)
    return schema


def validate_dataset(filename):
    if not os.path.exists(filename):
        return "File not found."

    with open(filename, "rb") as fp:
        try:
            data = json.load(fp)
        except json.JSONDecodeError as err:
            return "JSON decoding error: %s" % err.msg

    try:
        schema = load_schema()
    except FileNotFoundError:
        return "Schema file not found."

    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.ValidationError as err:
        return "JSONSchema validation error: %s" % err.msg

    if len(data["series"]) != data["n_dim"]:
        return "Number of dimensions and number of series don't match"

    if "time" in data.keys():
        if len(data["time"]["raw"]) != data["n_obs"]:
            return "Number of time points doesn't match number of observations"

    for var in data["series"]:
        if len(var["raw"]) != data["n_obs"]:
            return "Number of observations doesn't match for %s" % var["label"]

    return None


def get_name_from_dataset(filename):
    with open(filename, "rb") as fid:
        data = json.load(fid)
    return data["name"]


def dataset_is_demo(filename):
    with open(filename, "rb") as fid:
        data = json.load(fid)
    return "demo" in data.keys()


def get_demo_true_cps(name):
    dataset_dir = os.path.join(
        current_app.instance_path, current_app.config["DATASET_DIR"]
    )
    target_filename = os.path.join(dataset_dir, name + ".json")
    if not os.path.exists(target_filename):
        LOGGER.error("Dataset with name '%s' can't be found!" % name)
        return None
    with open(target_filename, "rb") as fid:
        data = json.load(fid)
    if not "demo" in data:
        LOGGER.error("Asked for 'demo' key in non-demo dataset '%s'" % name)
        return None
    if not "true_CPs" in data["demo"]:
        LOGGER.error(
            "Expected field'true_cps' field missing for dataset '%s'" % name
        )
    return data["demo"]["true_CPs"]


def md5sum(filename):
    """ Compute the MD5 hash for a given filename """
    blocksize = 65536
    hasher = hashlib.md5()
    with open(filename, "rb") as fid:
        buf = fid.read(blocksize)
        while len(buf) > 0:
            hasher.update(buf)
            buf = fid.read(blocksize)
    return hasher.hexdigest()


def load_data_for_chart(name, known_md5):
    dataset_dir = os.path.join(
        current_app.instance_path, current_app.config["DATASET_DIR"]
    )
    target_filename = os.path.join(dataset_dir, name + ".json")
    if not os.path.exists(target_filename):
        LOGGER.error("Dataset with name '%s' can't be found!" % name)
        return None
    if not md5sum(target_filename) == known_md5:
        LOGGER.error(
            """
        MD5 checksum failed for dataset with name: %s.
        Found: %s.
        Expected: %s.
        """
            % (name, md5sum(target_filename), known_md5)
        )
        return None
    with open(target_filename, "rb") as fid:
        data = json.load(fid)

    chart_data = {"time": data["time"] if "time" in data else None, "values": 
            data["series"]}
    return {"chart_data": chart_data}
