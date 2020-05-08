# -*- coding: utf-8 -*-

# Author: G.J.J. van den Burg <gvandenburg@turing.ac.uk>
# License: See LICENSE file
# Copyright: 2020 (c) The Alan Turing Institute

from functools import wraps

from flask import current_app, request, redirect, flash, url_for
from flask_login import current_user
from flask_login.config import EXEMPT_METHODS


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.config.get("LOGIN_DISABLED"):
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not current_user.is_confirmed:
            return redirect(url_for("auth.not_confirmed"))
        elif not current_user.is_admin:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)

    return decorated_view


def login_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.config.get("LOGIN_DISABLED"):
            return func(*args, **kwargs)
        elif not current_user.is_authenticated:
            return current_app.login_manager.unauthorized()
        elif not current_user.is_confirmed:
            return redirect(url_for("auth.not_confirmed"))
        return func(*args, **kwargs)

    return decorated_view
