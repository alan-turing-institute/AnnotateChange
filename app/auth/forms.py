# -*- coding: utf-8 -*-

# Author: G.J.J. van den Burg <gvandenburg@turing.ac.uk>
# License: See LICENSE file
# Copyright: 2020 (c) The Alan Turing Institute

from flask import current_app, flash
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import (
    DataRequired,
    Email,
    EqualTo,
    Optional,
    ValidationError,
)

from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    fullname = StringField("Full Name (optional)", validators=[])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    toc = BooleanField(
        "I agree to the Terms and Conditions.", validators=[DataRequired()]
    )
    credit = BooleanField(
        "Check this box if you would like to be publically credited with having "
        "contributed to this work. By default, users will remain anonymous.",
        validators=[Optional()],
    )
    updated = BooleanField(
        "Check this box if you wish to be kept up to date with the "
        "progress of this work by email.",
        validators=[Optional()],
    )
    submit = SubmitField("Register")

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError(
                "Username already in use, please use a different one."
            )

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError(
                "Email address already in use, please use a different one."
            )
        if current_app.config["USER_EMAILS"]:
            if email.data in current_app.config["USER_EMAILS"]:
                return
        if current_app.config["USER_EMAIL_DOMAINS"]:
            if (
                not email.data.split("@")[-1]
                in current_app.config["USER_EMAIL_DOMAINS"]
            ):
                raise ValidationError(
                    "Access to AnnotateChange is restricted to "
                    "individuals with email addresses from specific "
                    "institutions. Please use your employee email address "
                    "when signing up. If that does not solve the issue, "
                    "you unfortunately do not have access to "
                    "AnnotateChange at this time."
                )

    def validate_credit(self, credit):
        if credit.data and not self.fullname.data:
            flash(
                "Please provide your full name if you wish to "
                "be credited with contributing to this work.", "error")
            raise ValidationError(
                "Please provide your full name if you wish to "
                "be credited with contributing to this work."
            )


class ResetPasswordRequestForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    submit = SubmitField("Request password reset")


class ResetPasswordForm(FlaskForm):
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Request Password Reset")
