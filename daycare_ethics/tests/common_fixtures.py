# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Non-trivial fixtures that may be used across multiple suites.
"""

from unittest import TestCase

from .. import create_app


class FixtureConfiguration (object):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    TESTING = True


class BaseFixture (TestCase):
    def setUp(self):
        self.app = create_app(config_obj=FixtureConfiguration).test_client()
