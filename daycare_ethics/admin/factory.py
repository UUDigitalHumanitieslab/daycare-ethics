# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Admin factory for use with the main Flask application.
"""

from flask.ext.admin import Admin
from flask.ext.admin.contrib.sqla import ModelView

from ..database import models, db
from .views import *


def create_admin(app):
    """ Create an Admin object on Flask instance `app` and return it.
    """
    admin = Admin(name='Daycare Ethics')
    ses = db.session
    admin.add_view(MediaView(ses))
    admin.add_view(ModelView(models.Case, ses, 'Cases'))
    admin.add_view(ModelView(models.Vote, ses, 'Votes'))
    admin.add_view(ModelView(models.BrainTeaser, ses, 'Brain teasers'))
    admin.add_view(ModelView(models.Response, ses, 'Discussion'))
    admin.add_view(ModelView(models.Link, ses, 'Links'))
    admin.init_app(app)
    return admin
