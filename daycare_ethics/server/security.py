# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Captcha functionality common to some of the public views.
"""

from datetime import datetime, timedelta
from random import SystemRandom
from functools import wraps

from flask import current_app, session, request, jsonify, abort, json


QUARANTINE_TIME = timedelta(minutes=30)
AUTHENTICATION_TIME = timedelta(minutes=2)
HUMAN_LAG = timedelta(milliseconds=200)
KEY_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
KEY_LENGTH = 30
NORMALS = 7
ODDBALLS = 3


def init_app(app):
    data = json.load(open(app.config['CAPTCHA_DATA']))
    app.captcha_data = map(set, data.values())


def generate_key(generator):
    return ''.join((generator.choice(KEY_CHARS) for i in range(KEY_LENGTH)))


def init_captcha():
    dice = SystemRandom()
    normalset, oddballset = dice.sample(current_app.captcha_data, 2)
    normals = dice.sample(normalset, NORMALS)
    oddballs = dice.sample(oddballset - normalset, ODDBALLS)
    united = normals + oddballs
    dice.shuffle(united)
    challenge = ' '.join(united)
    expiry = datetime.today() + AUTHENTICATION_TIME
    session['captcha-answer'] = map(lambda s: s.lower(), oddballs)
    session['captcha-expires'] = expiry
    if 'captcha-quarantine' in session:
        del session['captcha-quarantine']
        session.modified = True
    return {'captcha_expires': str(expiry), 'captcha_challenge': challenge}


def authorize_captcha():
    now = datetime.today()
    if 'ca' not in request.form:
        return False
    if session['captcha-expires'] < now:
        return False
    answerlist = request.form['ca'].strip().lower().split()
    if set(session['captcha-answer']) == set(answerlist):
        return True
    return False


def captcha_safe():
    now = datetime.today()
    if 'captcha-answer' in session:
        authorized = authorize_captcha()
        del session['captcha-answer'], session['captcha-expires']
        if authorized:
            return True
        session['captcha-quarantine'] = now + QUARANTINE_TIME
        session.permanent = True
        return False
    if 'captcha-quarantine' in session:
        if now > session['captcha-quarantine']:
            del session['captcha-quarantine']
            session.modified = True
            return True
        return False
    return True


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
    @wraps(view)
    def wrap(**kwargs):
        now = datetime.today()
        return tokenize_response(view(**kwargs), now)
    return wrap


def session_protect(view):
    @wraps(view)
    def wrap(**kwargs):
        now = datetime.today()
        verify_natural()
        if ('token' not in session or 't' not in request.form
             or request.form['t'] != session['token']
             or datetime.today() - session['last-request'] < HUMAN_LAG ):
            session['tainted'] = True
            abort(400)
        return tokenize_response(view(**kwargs), now)
    return wrap
