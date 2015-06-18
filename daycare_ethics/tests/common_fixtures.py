# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Non-trivial fixtures that may be used across multiple suites.
"""

from os.path import dirname, join
from unittest import TestCase

from .. import create_app, db


class FixtureConfiguration (object):
    SQLALCHEMY_DATABASE_URI = 'sqlite://'
    CAPTCHA_DATA = join(dirname(__file__), 'data', 'test_captcha.json')
    SECRET_KEY = 'psiodfnvpsdojfnvpaosihrgt'
    TESTING = True


class BaseFixture (TestCase):
    def setUp(self):
        self.app = create_app(config_obj=FixtureConfiguration)
        self.client = self.app.test_client()

    def tearDown(self):
        db.drop_all(app=self.app)

    def request_context(self):
        return self.app.test_request_context()
