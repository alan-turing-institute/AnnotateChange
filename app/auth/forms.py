# -*- coding: utf-8 -*-

from flask import current_app
from flask_wtf import FlaskForm

from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo

from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
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
            if not email.data in current_app.config["USER_EMAIL_DOMAINS"]:
                raise ValidationError(
                    "Access to AnnotateChange is restricted to "
                    "individuals with email addresses from specific "
                    "institutions. Please use your employee email address "
                    "when signing up. If that does not solve the issue, "
                    "you unfortunately do not have access to "
                    "AnnotateChange at this time."
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
