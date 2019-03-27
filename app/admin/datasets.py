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

import json
import hashlib


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
