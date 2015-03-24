# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Captcha functionality common to some of the public views.
"""

import json
from datetime import datetime, timedelta
from random import SystemRandom

from flask import current_app, session, request, jsonify, abort


AUTHENTICATION_TIME = timedelta(minutes=2)
HUMAN_LAG = timedelta(milliseconds=200)
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


def verify_natural():
    if ( not request.is_xhr
         or 'User-Agent' not in request.headers
         or request.headers['User-Agent'] == ''
         or 'Referer' not in request.headers
         or request.headers['Referer'] == '' ):
        session['tainted'] = True
        abort(400)
    if 'tainted' in session:
        abort(400)


def tokenize_response(response, request_start):
    key = generate_key(SystemRandom())
    session['token'] = key
    session['last-request'] = request_start
    if isinstance(response, tuple):
        if len(response) == 3:
            return jsonify(token=key, **response[0]), response[1], response[2]
        if len(response) == 2:
            return jsonify(token=key, **response[0]), response[1]
        return jsonify(token=key, **response[0])
    return jsonify(token=key, **response)


def session_enable(view):
    def wrap(**kwargs):
        now = datetime.today()
        verify_natural()
        return tokenize_response(view(**kwargs), now)
    return wrap


def session_protect(view):
    def wrap(**kwargs):
        now = datetime.today()
        verify_natural()
        if (session.new or 't' not in request.form
             or request.form['t'] != session['token']
             or datetime.today() - session['last-request'] < HUMAN_LAG ):
            session['tainted'] = True
            abort(400)
        return tokenize_response(view(**kwargs), now)
    return wrap
