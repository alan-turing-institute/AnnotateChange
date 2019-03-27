# -*- coding: utf-8 -*-

from app import create_app, db, cli

app = create_app()
cli.register(app)
