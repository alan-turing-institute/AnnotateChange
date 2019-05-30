# -*- coding: utf-8 -*-

"""
Dataset handling

The dataset model is a JSON object as follows:

    {
        "name": "name of the dataset",
        "n_obs": number of observations,
        "n_dim": number of dimensions,
        "series": {
            "V1": {
                "type": "float",
                "raw": [list of observations]
                },
            "V2": {
                "type": "int",
                "raw": [list of observations]
            },
            "V3": {
                "type": "category",
                "levels": ["A", "B", "C"],
                "raw": [list of observations]
                }
            }
    }

Missing values must be denoted by 'NaN' (this is understood by the JSON 
decoder).

Author: Gertjan van den Burg

"""

import hashlib
import json
import logging
import os
import re

from flask import current_app

LOGGER = logging.getLogger(__file__)


def validate_dataset(filename):
    """ Validate a dataset uploaded to the webapp
    Return None on success and a string error on failure
    """

    with open(filename, "rb") as fid:
        try:
            data = json.load(fid)
        except json.JSONDecodeError as err:
            return "JSON decoding error: %s" % err.msg

    required_keys = ["name", "n_obs", "n_dim", "series"]
    for key in required_keys:
        if not key in data:
            return "Required key missing: %s" % key

    if not re.fullmatch("\w+", data["name"]):
        return "Name can only contain characters in the set [a-zA-Z0-9_]"

    if len(data["series"]) != data["n_dim"]:
        return "Number of dimensions and number of series don't match"

    required_keys = ["type", "raw"]
    for idx, var in enumerate(data["series"]):
        if not var == "V%i" % (idx + 1):
            return "Unexpected variable name, expected 'V<int>', got %s" % var
        vardict = data["series"][var]
        for key in required_keys:
            if not key in vardict:
                return "Key '%s' missing for variable '%s'" % (key, var)
        if vardict["type"] == "category":
            if not "levels" in vardict:
                return (
                    "Variable '%s' has categorical type but 'levels' is missing"
                    % (var)
                )
        if not len(vardict["raw"]) == data["n_obs"]:
            return (
                "Length of data for variable '%s' not equal to n_obs = %i"
                % (var, data["n_obs"])
            )

    return None


def get_name_from_dataset(filename):
    with open(filename, "rb") as fid:
        data = json.load(fid)
    return data["name"]


def dataset_is_demo(filename):
    with open(filename, "rb") as fid:
        data = json.load(fid)
    return "demo" in data


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
    chart_data = [{"value": x} for x in data["series"]["V1"]["raw"]]
    return {"chart_data": chart_data}
