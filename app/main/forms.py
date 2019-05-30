# -*- coding: utf-8 -*-

from flask_wtf import FlaskForm

from wtforms import SubmitField

class NextForm(FlaskForm):
    submit = SubmitField("Continue")
