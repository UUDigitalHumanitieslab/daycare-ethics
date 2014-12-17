# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""

"""

from unittest import TestCase

from ...database.util import InnoDBSQLAlchemy

class TableArgsMetaTestCase (TestCase):
    def setUp(self):
        self.db = InnoDBSQLAlchemy()

    def test_dictionary(self):
        class Derived (self.db.Model):
            id = self.db.Column(self.db.Integer, primary_key=True)
        instance = Derived()
        self.assertEqual(instance.__table_args__['mysql_engine'], 'InnoDB')

    def test_tuple_notrailingdict(self):
        class Derived (self.db.Model):
            __table_args__ = ()
            id = self.db.Column(self.db.Integer, primary_key=True)
        instance = Derived()
        self.assertEqual(instance.__table_args__[-1]['mysql_engine'], 'InnoDB')

    def test_tuple_trailingdict(self):
        class Derived (self.db.Model):
            __table_args__ = ({},)
            id = self.db.Column(self.db.Integer, primary_key=True)
        instance = Derived()
        self.assertEqual(instance.__table_args__[-1]['mysql_engine'], 'InnoDB')

