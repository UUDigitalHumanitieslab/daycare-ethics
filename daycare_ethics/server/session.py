# (c) 2015 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Server-side session support.
"""

import flask.sessions as fs

from ..database import models as m


class Session(dict, fs.SessionMixin):
    """ Vehicle for our server-side session objects. """
    former = None
    new = True


class SessionInterface(fs.SessionInterface):
    """ The server-side replacement implementation for session handling. """
    
    session_class = Session
    pickle_based = True
    
    def open_session(self, app, request):
        s = Session()
        cookie_name = app.config['SESSION_COOKIE_NAME']
        alleged_token = None
        if 't' in request.form:
            alleged_token = request.form['t']
        elif cookie_name in request.cookies:
            alleged_token = request.cookies[cookie_name]
        if alleged_token is not None:
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
                httponly=app.config['SESSION_COOKIE_HTTPONLY']
            )
