# -*- coding: utf-8 -*-

# Author: G.J.J. van den Burg <gvandenburg@turing.ac.uk>
# License: See LICENSE file
# Copyright: 2020 (c) The Alan Turing Institute

from flask_wtf import FlaskForm

from wtforms import SubmitField

class NextForm(FlaskForm):
    submit = SubmitField("Continue")
