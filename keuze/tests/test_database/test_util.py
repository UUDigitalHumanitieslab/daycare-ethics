# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""

"""

from unittest import TestCase

import flask.ext.sqlalchemy as fsqla

from ...database import db

class TableArgsMetaTestCase (TestCase):
    def test_dictionary (self):
        class Derived (db.Model):
            id = db.Column(db.Integer, primary_key=True)
        instance = Derived()
        self.assertEqual(instance.__table_args__['mysql_engine'], 'InnoDB')

    def test_tuple_notrailingdict (self):
        class Derived (db.Model):
            __table_args__ = ()
            id = db.Column(db.Integer, primary_key=True)
        instance = Derived()
        self.assertEqual(instance.__table_args__['mysql_engine'], 'InnoDB')

    def test_tuple_trailingdict (self):
        class Derived (db.Model):
            __table_args__ = ({},)
            id = db.Column(db.Integer, primary_key=True)
        instance = Derived()
        self.assertEqual(instance.__table_args__['mysql_engine'], 'InnoDB')

