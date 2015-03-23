# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Captcha functionality common to some of the public views.
"""

import json
from datetime import datetime, timedelta
from random import SystemRandom

from flask import current_app, session, request


AUTHENTICATION_TIME = timedelta(minutes=2)
KEY_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
KEY_LENGTH = 30
NORMALS = 7
ODDBALLS = 3



def init_app(app):
    app.captcha_data = map(set, json.load(app.config['CAPTCHA_DATA']).values())


def generate_key(generator):
    return ''.join((generator.choice(KEY_CHARS) for i in range(KEY_LENGTH)))


def init_captcha():
    dice = SystemRandom()
    normalset, oddballset = dice.sample(current_app.captcha_data, 2)
    normals = dice.sample(normalset, NORMALS)
    oddballs = dice.sample(oddballset - normalset, ODDBALLS)
    challenge = ' '.join(dice.shuffle(normals + oddballs))
    expiry = datetime.today() + AUTHENTICATION_TIME
    session['captcha-answer'] = oddballs
    session['captcha-expires'] = expiry
    session.modified = True
    return {'captcha-expires': str(expiry), 'captcha-challenge': challenge}


def authorize_captcha():
    now = datetime.today()
    if 'captcha-expires' not in session or 'captcha-answer' not in session:
        return False
    if 'ca' not in request.form:
        return False
    if session['captcha-expires'] < now:
        return False
    answerlist = request.form['ca'].strip().lower().split()
    if set(session['captcha-answer']) == set(answerlist):
        return True
    return False
