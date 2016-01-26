# (c) 2014, 2015 Digital Humanities Lab, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from datetime import datetime
from unittest import TestCase

from ..common_fixtures import BaseFixture
from ...database import db
from ...database.models import *


class SQLADeclaredAttrTestCase(TestCase):
    def test_picture_refs(self):
        self.assertIn('picture', Case.__dict__)

    def test_picture_backrefs(self):
        self.assertIn('cases', Picture.__dict__)


class ModelsAreCreatedTestCase(BaseFixture):
    def test_session_exists(self):
        ses = Session(token='1234567890')
        with self.request_context():
            db.session.add(ses)
            db.session.commit()
            first = db.session.query(Session).first()
        self.assertEqual(first.token, '1234567890')
        self.assertEqual(first, ses)

    def test_picture_exists(self):
        pic = Picture(mime_type='image/jpeg', name='Test', path='test/test.jpeg')
        with self.request_context():
            db.session.add(pic)
            db.session.commit()
            first = db.session.query(Picture).first()
        self.assertEqual(pic.id, 1)
        self.assertEqual(first, pic)

    def test_case_exists(self):
        case = Case(title='Test')
        with self.request_context():
            db.session.add(case)
            db.session.commit()
            first = db.session.query(Case).first()
        self.assertEqual(case.id, 1)
        self.assertEqual(first, case)

    def test_vote_exists(self):
        case = Case(title='Test')
        vote = Vote(submission=datetime.now(), agree=True, case=case)
        with self.request_context():
            db.session.add(vote)
            db.session.commit()
            first = db.session.query(Vote).first()
        self.assertEqual(vote.id, 1)
        self.assertEqual(first, vote)

    def test_brain_teaser_exists(self):
        bt = BrainTeaser(title='Test')
        with self.request_context():
            db.session.add(bt)
            db.session.commit()
            first = db.session.query(BrainTeaser).first()
        self.assertEqual(bt.id, 1)
        self.assertEqual(first, bt)

    def test_response_exists(self):
        bt = BrainTeaser(title='Test')
        rsp = Response( submission=datetime.now(),
                        pseudonym='test',
                        brain_teaser=bt,
                        message='bla' )
        with self.request_context():
            db.session.add(rsp)
            db.session.commit()
            first = db.session.query(Response).first()
        self.assertEqual(rsp.id, 1)
        self.assertEqual(first, rsp)

    def test_tip_exists(self):
        now = datetime.now()
        tip = Tip(create=now, update=now, title='test')
        with self.request_context():
            db.session.add(tip)
            db.session.commit()
            first = db.session.query(Tip).first()
        self.assertEqual(tip.id, 1)
        self.assertEqual(first, tip)
