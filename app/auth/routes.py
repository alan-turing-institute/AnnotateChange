# -*- coding: utf-8 -*-

import datetime

from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user

from werkzeug.urls import url_parse

from app import db
from app.auth import bp

from app.auth.forms import (
    LoginForm,
    RegistrationForm,
    ResetPasswordRequestForm,
    ResetPasswordForm,
)
from app.auth.email import (
    send_password_reset_email,
    send_email_confirmation_email,
)
from app.models import User


@bp.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password", "error")
            return redirect(url_for("auth.login"))
        login_user(user, remember=form.remember_me.data)
        current_user.last_active = datetime.datetime.utcnow()
        db.session.commit()
        if not user.is_confirmed:
            return redirect(url_for("auth.not_confirmed"))
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            next_page = url_for("main.index")
        return redirect(next_page)
    return render_template("auth/login.html", title="Sign In", form=form)


@bp.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("main.index"))


@bp.route("/register", methods=("GET", "POST"))
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        send_email_confirmation_email(user)
        flash(
            "An email has been sent to confirm your account, please check your email (including the spam folder).",
            "info",
        )

        return redirect(url_for("auth.login"))
    return render_template("auth/register.html", title="Register", form=form)


@bp.route("/reset_password_request", methods=("GET", "POST"))
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(
            "Please check your email for the instructions to reset your password.",
            "info",
        )
        return redirect(url_for("auth.login"))
    return render_template(
        "auth/reset_password_request.html", title="Reset Password", form=form
    )


@bp.route("/reset_password/<token>", methods=("GET", "POST"))
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for("main.index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash("Your password has been reset.", "info")
        return redirect(url_for("auth.login"))
    return render_template("auth/reset_password.html", form=form)


@bp.route("/confirm/<token>")
def confirm_email(token):
    if current_user.is_authenticated and current_user.is_confirmed:
        flash("Account is already confirmed.")
        return redirect(url_for("main.index"))
    user = User.verify_email_confirmation_token(token)
    if not user:
        flash("The confirmation link is invalid or has expired.", "error")
        return redirect(url_for("main.index"))
    if user.is_confirmed:
        flash("Account is already confirmed, please login.", "success")
    else:
        user.is_confirmed = True
        db.session.commit()
        flash("Account confirmed successfully. Thank you!", "success")
        return redirect(url_for("auth.login"))
    return redirect(url_for("main.index"))


@bp.route("/not_confirmed")
def not_confirmed():
    if current_user.is_anonymous:
        flash("Please login before accessing this page.")
        return redirect(url_for("auth.login"))
    if current_user.is_confirmed:
        flash("Account is already confirmed.")
        return redirect(url_for("main.index"))
    flash("Please confirm your account before moving on.", "info")
    return render_template("auth/not_confirmed.html")


@bp.route("/resend")
def resend_confirmation():
    if current_user.is_anonymous:
        flash("Please login before accessing this page.")
        return redirect(url_for("auth.login"))
    if current_user.is_confirmed:
        flash("Account is already confirmed.")
        return redirect(url_for("main.index"))
    send_email_confirmation_email(current_user)
    email = current_user.email
    flash("A new confirmation has been sent to %s." % email, "success")
    return redirect(url_for("auth.not_confirmed"))
