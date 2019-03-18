# -*- coding: utf-8 -*-

from functools import wraps

from flask import current_app, request
from flask_login import current_user
from flask_login.config import EXEMPT_METHODS


def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if request.method in EXEMPT_METHODS:
            return func(*args, **kwargs)
        elif current_app.config.get("LOGIN_DISABLED"):
            return func(*args, **kwargs)
        elif not current_user.is_admin:
            return current_app.login_manager.unauthorized()
        return func(*args, **kwargs)

    return decorated_view
