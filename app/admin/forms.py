# -*- coding: utf-8 -*-

# Author: G.J.J. van den Burg <gvandenburg@turing.ac.uk>
# License: See LICENSE file
# Copyright: 2020 (c) The Alan Turing Institute

import os

from flask import current_app
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired

from wtforms import SubmitField, SelectField
from wtforms.validators import ValidationError, InputRequired

from werkzeug.utils import secure_filename

from app.models import Dataset
from app.utils.datasets import validate_dataset, get_name_from_dataset


class AdminManageTaskForm(FlaskForm):
    username = SelectField(
        "Username", coerce=int, validators=[InputRequired()]
    )
    dataset = SelectField("Dataset", coerce=int, validators=[InputRequired()])
    assign = SubmitField("Assign")
    delete = SubmitField("Delete")


class AdminAddDatasetForm(FlaskForm):
    file_ = FileField("File", validators=[FileRequired()])
    submit = SubmitField("Upload")

    def validate_file_(self, field):
        filename = secure_filename(field.data.filename)
        if not "." in filename:
            raise ValidationError("The file should be a '.json' file.")
        if not filename.rsplit(".", 1)[1].lower() == "json":
            raise ValidationError("The file should be a '.json' file.")

        temp_filename = os.path.join(
            current_app.instance_path, current_app.config["TEMP_DIR"], filename
        )

        field.data.save(temp_filename)
        error = validate_dataset(temp_filename)
        if not error is None:
            os.unlink(temp_filename)
            raise ValidationError("Error validating dataset: %s" % error)

        name = get_name_from_dataset(temp_filename)
        dataset = Dataset.query.filter_by(name=name).first()
        if dataset is not None:
            os.unlink(temp_filename)
            raise ValidationError(
                "A dataset with the name '%s' already exists." % name
            )


class AdminManageDatasetsForm(FlaskForm):
    dataset = SelectField("Dataset", coerce=int, validators=[InputRequired()])
    delete = SubmitField("Delete")


class AdminManageUsersForm(FlaskForm):
    user = SelectField("User", coerce=int, validators=[InputRequired()])
    delete = SubmitField("Delete")


class AdminSelectDatasetForm(FlaskForm):
    dataset = SelectField("Dataset", coerce=int, validators=[InputRequired()])
    submit = SubmitField("Show")
