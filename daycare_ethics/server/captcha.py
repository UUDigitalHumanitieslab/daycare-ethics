# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Captcha functionality common to some of the public views.
"""

import json
from datetime import datetime, timedelta
from random import SystemRandom

from flask import current_app

from ..database import db
from ..database.models import Token


AUTHENTICATION_TIME = timedelta(minutes=2)
EXPIRATION_TIME = timedelta(days=31)
KEY_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
KEY_LENGTH = 30
NORMALS = 7
ODDBALLS = 3


def init_app(app):
    app.captcha_data = map(set, json.load(app.config['CAPTCHA_DATA']).values())
    cleanup_cache(app)


def cleanup_cache(app):
    expiry_date = datetime.today() - EXPIRATION_TIME
    with app.request_context():
        Token.query.filter(Token.date <= expiry_date).delete()


def generate_key(generator):
    return ''.join((generator.choice(KEY_CHARS) for i in range(KEY_LENGTH)))


def create():
    dice = SystemRandom()
    key = generate_key(dice)
    normalset, oddballset = dice.sample(current_app.captcha_data, 2)
    normals = dice.sample(normalset, NORMALS)
    oddballs = dice.sample(oddballset - normalset, ODDBALLS)
    challenge = ' '.join(dice.shuffle(normals + oddballs))
    solution = ' '.join(oddballs)
    now = datetime.today()
    expiry = now + EXPIRATION_TIME
    db.session.add(Token(id=key, date=now, answer=solution))
    db.session.commit()
    return jsonify(token=key, expires=expiry, challenge=challenge)


def revoke(token):
    db.session.delete(token)
    db.session.commit()


def authorize(key):
    now = datetime.today()
    token = Token.get(key)
    if not token:
        return 'hackattempt'
    if token.date <= now - EXPIRATION_TIME:
        revoke(token)
        return False
    if token.authorized:
        return True
    if token.date <= now - AUTHENTICATION_TIME:
        revoke(token)
        return False
    