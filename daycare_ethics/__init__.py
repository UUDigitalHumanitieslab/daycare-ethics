# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Head of the serverside application package.

    This module provides the WSGI application factory.
"""

from flask import Flask

from .database import db
from .server import public
from .admin import create_admin


def create_app(config_file=None, config_obj=None):
    app = Flask(__name__, static_folder='www', static_url_path='')
    if config_file is not None:
        app.config.from_pyfile(config_file)
    elif config_obj is not None:
        app.config.from_object(config_obj)
    else:
        raise TypeError('no configuration argument provided')

    db.init_app(app)
    db.create_all(app=app)  # pass app because of Flask-SQLAlchemy contexts
    app.register_blueprint(public)
    create_admin(app)

    return app
