# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from unittest import TestCase

from ..common_fixtures import BaseFixture
from ...database import db
from ...database.models import *


class SQLADeclaredAttrTestCase(TestCase):
    def test_picture_refs(self):
        self.assertIn('picture', Case.__dict__)
        self.assertIn('picture', BrainTeaser.__dict__)

    def test_picture_backrefs(self):
        self.assertIn('cases', Picture.__dict__)
        self.assertIn('brain_teasers', Picture.__dict__)


class ModelsAreCreatedTestCase(BaseFixture):
    def test_picture_exists(self):
        pic = Picture(mime_type='image/jpeg', name='Test', path='test/test.jpeg')
        with self.request_context():
            db.session.add(pic)
            db.session.commit()
            self.assertEqual(pic.id, 1)
            self.assertEqual(Picture.query.first(), pic)
