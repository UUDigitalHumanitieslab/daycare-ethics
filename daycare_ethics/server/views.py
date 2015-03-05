# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Directly visitable routes on the domain.
"""

from datetime import date

from flask import send_from_directory, jsonify

from ..database.models import Case
from blueprint import public


@public.route('/')
def index():
    return send_from_directory(public.static_folder, 'index.html')


@public.route('/case/')
def current_casus():
    latest_casus = (
        Case.query
        .filter(Case.publication <= date.today())
        .order_by(Case.publication.desc())
        .first()
    )
    if latest_casus.publication:
        publication = latest_casus.publication.isoformat()
        week = latest_casus.publication.strftime('%W')
    else:
        publication = None
        week = None
    if latest_casus.closure:
        closure = latest_casus.closure.isoformat()
    else:
        closure = None
    return jsonify(
        id=latest_casus.id,
        title=latest_casus.title,
        publication=publication,
        week=week,
        closure=closure,
        text=latest_casus.text,
        proposition=latest_casus.proposition,
        picture=latest_casus.picture_id,
        background=latest_casus.background )