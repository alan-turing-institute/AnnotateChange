# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo


class AdminAssignTaskForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    dataset = StringField("Dataset", validators=[DataRequired()])
    submit = SubmitField("Assign")
