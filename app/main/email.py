# -*- coding: utf-8 -*-

# Author: G.J.J. van den Burg <gvandenburg@turing.ac.uk>
# License: See LICENSE file
# Copyright: 2020 (c) The Alan Turing Institute

import json

from flask import current_app, render_template

from app.email import send_email


def send_annotation_backup(record):
    pretty_record = json.dumps(record, sort_keys=True, indent=4)
    subject = "[Backup] New Annotation Recorded"
    if current_app.debug:
        subject += " (debug)"
    send_email(
        subject,
        sender=current_app.config["ADMINS"][0],
        recipients=[current_app.config["ADMINS"][0]],
        text_body=render_template(
            "email/annotation_record.txt", pretty_record=pretty_record
        ),
        html_body=render_template(
            "email/annotation_record.html", pretty_record=pretty_record
        ),
    )
