# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Object relational model and database schema.
    
    An organogram will be provided as external documentation of the
    database structure.
"""

import os

from flask import current_app
from sqlalchemy.event import listens_for

from ..util import image_variants
from db import db


class Picture (db.Model):
    """ Image or video for illustration of a case or brain teaser.
    """
    id          = db.Column(db.Integer, primary_key=True)
    mime_type   = db.Column(db.String(30), nullable=False)
    name        = db.Column(db.String(40), nullable=False)
    path        = db.Column(db.String(50), unique=True, nullable=False)


@listens_for(Picture, 'after_delete')
def del_file(mapper, connection, target):
    if target.path:
        directory = current_app.instance_path
        for path in [target.path] + image_variants(target.path):
            try:
                os.remove(os.path.join(directory, path))
            except OSError:
                # Don't care if was not deleted because it does not exist
                pass


class PublicationItem (object):
    """ Common properties of things that are published periodically.
    """
    id          = db.Column(db.Integer, primary_key=True)
    publication = db.Column(db.Date)
    closure     = db.Column(db.Date)
    title       = db.Column(db.Text)
    text        = db.Column(db.Text)
    
    def __str__(self):
        return self.title


class Case (PublicationItem, db.Model):
    """ Weekly moral issue with a proposition that users can vote on.
    """
    __tablename__   = 'case'
    picture_id      = db.Column(db.ForeignKey('picture.id'))
    proposition     = db.Column(db.Text)
    yes_votes       = db.Column(db.Integer, default=0)
    no_votes        = db.Column(db.Integer, default=0)
    background      = db.Column(db.String(7))  # an RGB color code
    picture         = db.relationship('Picture', backref='cases')


class Vote (db.Model):
    """ Vote on a case proposition, either agree (True) or don't agree (False).
    """
    id          = db.Column(db.Integer, primary_key=True)
    case_id     = db.Column(db.ForeignKey('case.id'), nullable=False)
    submission  = db.Column(db.DateTime, nullable=False)
    agree       = db.Column(db.Boolean, nullable=False)
    case        = db.relationship('Case', backref='votes')


class BrainTeaser (PublicationItem, db.Model):
    """ Periodic reflection item that users may discuss publicly.
    """
    __tablename__   = 'brain_teaser'


class Response (db.Model):
    """ Response to the discussion associated with a brain teaser.
    """
    id              = db.Column(db.Integer, primary_key=True)
    brain_teaser_id = db.Column(db.ForeignKey('brain_teaser.id'), nullable=False)
    submission      = db.Column(db.DateTime, nullable=False)
    pseudonym       = db.Column(db.String(30), nullable=False)
    upvotes         = db.Column(db.Integer, default=0)
    downvotes       = db.Column(db.Integer, default=0)
    message         = db.Column(db.Text, nullable=False)
    brain_teaser    = db.relationship('BrainTeaser', backref='responses')


class Tip (db.Model):
    """ Any reference that the content provider opts to share with users.
    """
    id      = db.Column(db.Integer, primary_key=True)
    create  = db.Column(db.DateTime, nullable=False)
    update  = db.Column(db.DateTime, nullable=False)
    what    = db.Column(db.Enum('labour code', 'book', 'site'))
    author  = db.Column(db.Text)
    title   = db.Column(db.Text, nullable=False)
    text    = db.Column(db.Text)
    href    = db.Column(db.Text)


class Token (db.Model):
    """ Authorization tokens for the CAPTCHAs.
    """
    id = db.Column(db.String(30), primary_key=True)
    date = db.Column(db.DateTime, nullable=False)
    authorized = db.Column(db.Boolean, default=False)
    answer = db.Column(db.Text)
