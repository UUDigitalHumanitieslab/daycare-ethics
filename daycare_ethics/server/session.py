# (c) 2015 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Server-side session support.
"""

import random

import flask.sessions as fs

from ..database import models as m


KEY_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
KEY_LENGTH = 30  # WARNING: this is also hardcoded in ..database.models.Session
                 # so you have to update the key length in two places!


def generate_key():
    rng = random.SystemRandom()
    return ''.join((rng.choice(KEY_CHARS) for i in range(KEY_LENGTH)))


class Session(dict, fs.SessionMixin):
    """ Vehicle for our server-side session objects. """
    former = None
    new = True
    
    def renew_token(self):
        key = generate_key()
        self['token'] = key
        return key
    
    def __init__(self):
        super(Session, self).__init__()
        self.renew_token()


class SessionInterface(fs.SessionInterface):
    """ The server-side replacement implementation for session handling. """
    
    session_class = Session
    pickle_based = True
    
    def open_session(self, app, request):
        s = Session()
        cookie_name = app.config['SESSION_COOKIE_NAME']
        alleged_token = None
        if 't' in request.values:
            alleged_token = request.values['t']
        elif cookie_name in request.cookies:
            alleged_token = request.cookies[cookie_name]
        if alleged_token is not None and len(alleged_token) <= KEY_LENGTH:
            data = m.Session.query.get(alleged_token)
            if data:
                s.update(data.payload)
                s.former = data
                s.new = False
            else:
                s['tainted'] = True
                s['token'] = alleged_token
                s.permanent = True
        return s
    
    def save_session(self, app, session, response):
        cookie_name = app.config['SESSION_COOKIE_NAME']
        max_lifetime = app.config['PERMANENT_SESSION_LIFETIME']
        expires = self.get_expiration_time(app, session)
        if session.modified and 'token' in session:
            db_session = app.extensions['sqlalchemy'].db.session
            if session.former != None:
                db_session.delete(session.former)
            db_session.add(m.Session(
                token=session['token'],
                expires=expires,
                payload=dict(session)
            ))
            db_session.commit()
            response.set_cookie(
                cookie_name,
                value=session['token'],
                max_age=max_lifetime if session.permanent else None,
                httponly=app.config['SESSION_COOKIE_HTTPONLY'],
                path=app.config['APPLICATION_ROOT']
            )
