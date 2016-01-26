# (c) 2014, 2015 Digital Humanities Lab, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Admin factory for use with the main Flask application.
"""

from flask.ext.admin import Admin

from ..database import models, db
from .views import *


def create_admin(app):
    """ Create an Admin object on Flask instance `app` and return it.
    """
    admin = Admin(name='Daycare Ethics')
    ses = db.session
    admin.add_view(MediaView(ses))
    admin.add_view(CasesView(ses))
    admin.add_view(VotesView(ses))
    admin.add_view(BrainTeasersView(ses))
    admin.add_view(ResponsesView(ses))
    admin.add_view(TipsView(ses))
    admin.init_app(app)
    return admin
