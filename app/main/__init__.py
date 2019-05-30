# -*- coding: utf-8 -*-

from flask import Blueprint

bp = Blueprint('main', __name__)

from app.main import routes, demo


