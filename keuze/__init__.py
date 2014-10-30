# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""

"""

from flask import Flask

from .database import db, models
from .server import public, views

def create_app (config):
    app = Flask(__name__, static_folder = 'www', static_url_path = '')
    app.config.from_object(config)
    
    db.init_app(app)
    db.create_all(app = app)  # pass app because of Flask-SQLAlchemy contexts
    app.register_blueprint(public)
    
    return app
