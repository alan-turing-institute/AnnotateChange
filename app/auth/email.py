# -*- coding: utf-8 -*-

from threading import Thread

from flask import current_app, render_template

from app import mail


def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(
        "[AnnotateChange] Reset your password",
        sender=current_app.config["ADMINS"][0],
        recipients=[user.email],
        text_body=render_template(
            "email/reset_password.txt", user=user, token=token
        ),
        html_body=render_template(
            "email/reset_password.html", user=user, token=token
        ),
    )
