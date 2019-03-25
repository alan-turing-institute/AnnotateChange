# -*- coding: utf-8 -*-

import os
import json

from flask import current_app


def load_data_for_chart(name):
    dataset_dir = os.path.join(
        current_app.instance_path, current_app.config["DATASET_DIR"]
    )
    target_filename = os.path.join(dataset_dir, name + ".json")
    with open(target_filename, 'rb') as fid:
        data = json.load(fid)
    chart_data = [{"value": x} for x in data['series']['V1']['raw']]
    return {"chart_data": chart_data}


