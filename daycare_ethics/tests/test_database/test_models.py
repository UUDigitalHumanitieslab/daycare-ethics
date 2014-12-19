# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from datetime import datetime
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
    def test_case_exists(self):
        case = Case(title='Test')
        with self.request_context():
            db.session.add(case)
            db.session.commit()
            self.assertEqual(case.id, 1)
            self.assertEqual(Case.query.first(), case)
    def test_vote_exists(self):
        case = Case(title='Test')
        vote = Vote(submission=datetime.now(), agree=True, case=case)
        with self.request_context():
            db.session.add(vote)
            db.session.commit()
            self.assertEqual(vote.id, 1)
            self.assertEqual(Vote.query.first(), vote)
    def test_brain_teaser_exists(self):
        bt = BrainTeaser(title='Test')
        with self.request_context():
            db.session.add(bt)
            db.session.commit()
            self.assertEqual(bt.id, 1)
            self.assertEqual(BrainTeaser.query.first(), bt)
    def test_response_exists(self):
        bt = BrainTeaser(title='Test')
        rsp = Response(submission=datetime.now(), pseudonym='test', brain_teaser=bt)
        with self.request_context():
            db.session.add(rsp)
            db.session.commit()
            self.assertEqual(rsp.id, 1)
            self.assertEqual(Response.query.first(), rsp)
    def test_link_exists(self):
        lnk = Link(date=datetime.now(), href='http://www.test.org')
        with self.request_context():
            db.session.add(lnk)
            db.session.commit()
            self.assertEqual(lnk.id, 1)
            self.assertEqual(Link.query.first(), lnk)
