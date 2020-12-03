# -*- coding: utf-8 -*-

# Author: G.J.J. van den Burg <gvandenburg@turing.ac.uk>
# License: See LICENSE file
# Copyright: 2020 (c) The Alan Turing Institute

import click
import getpass

from email_validator import validate_email

from app import db
from app.models import User


def register(app):
    @app.cli.group(help="Perform admin commands")
    def admin():
        pass

    @admin.command()
    @click.option("--auto-confirm-email", is_flag=True)
    def add(auto_confirm_email):
        username = input("Enter username: ")
        email = input("Enter email address: ")
        password = getpass.getpass()
        assert password == getpass.getpass("Repeat password: ")

        user = User.query.filter_by(username=username).first()
        if user is not None:
            raise ValueError("User already exists")

        validate_email(email)

        user = User(
            username=username,
            email=email,
            is_admin=True,
            is_confirmed=auto_confirm_email,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        print("Admin user %r added successfully." % username)
