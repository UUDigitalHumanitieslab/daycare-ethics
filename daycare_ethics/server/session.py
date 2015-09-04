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
        if 't' in request.form:
            data = m.Session.query.get(request.form['t'])
            if data:
                s.update(data.payload)
                s.former = data
                s.new = False
            else:
                s['tainted'] = True
        return s
    
    def save_session(self, app, session, response):
        if session.modified and 'token' in session:
            db_session = app.extensions['sqlalchemy'].db.session
            if session.former != None:
                db_session.delete(session.former)
            db_session.add(m.Session(
                token=session['token'],
                expires=self.get_expiration_time(app, session),
                payload=dict(session)
            ))
            db_session.commit()
