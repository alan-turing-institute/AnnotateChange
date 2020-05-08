# -*- coding: utf-8 -*-

# Author: G.J.J. van den Burg <gvandenburg@turing.ac.uk>
# License: See LICENSE file
# Copyright: 2020 (c) The Alan Turing Institute

from flask import Blueprint

bp = Blueprint("admin", __name__, url_prefix="/admin")

from app.admin import routes
