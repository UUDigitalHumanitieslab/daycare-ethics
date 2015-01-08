# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from datetime import datetime

from ..common_fixtures import BaseFixture
from ...database.models import *


class VotesViewTestCase(BaseFixture):
    def setUp(self):
        super(VotesViewTestCase, self).setUp()
        testcase = Case(title='Testcase')
        with self.request_context():
            db.session.add(Vote(case=testcase, submission=datetime.now(), agree=True))
            db.session.add(Vote(case=testcase, submission=datetime.now(), agree=False))
            db.session.add(Vote(case=testcase, submission=datetime.now(), agree=True))
            db.session.commit()

    def test_export_data(self):
        response = self.client.post(
            '/admin/vote/action/',
            content_type='application/x-www-form-urlencoded',
            data='action=Export&rowid=1&rowid=2&rowid=3' )
        self.assertTrue(
            response
            .headers['Content-Disposition']
            .startswith('attachment; filename="')
        )
        self.assertEqual(response.headers['Content-Type'], 'text/csv; charset=utf-8')
        self.assertRegexpMatches(
            response.data,
            'case;submission;agree\\r\\n' +
            'Testcase;\\d{4}(-\\d{2}){2} (\\d{2}:){2}\\d{2}(.\d+)?;True\\r\\n' +
            'Testcase;\\d{4}(-\\d{2}){2} (\\d{2}:){2}\\d{2}(.\d+)?;False\\r\\n' +
            'Testcase;\\d{4}(-\\d{2}){2} (\\d{2}:){2}\\d{2}(.\d+)?;True' )


class TipsViewTestCase(BaseFixture):
    def setUp(self):
        super(TipsViewTestCase, self).setUp()
        self.old_age = datetime(1968, 4, 4, 6, 1)
        with self.request_context():
            db.session.add(Tip(
                title='some book',
                what='book',
                create=self.old_age,
                update=self.old_age ))
            db.session.add(Tip(
                title='some website',
                create=self.old_age,
                update=self.old_age ))
            db.session.commit()

    def test_bump(self):
        response = self.client.post(
            '/admin/tip/action/',
            data = {
                'action': 'Bump',
                'rowid': '1',
            },
            follow_redirects=True )
        self.assertIn(' tips have been bumped.', response.data)
        with self.request_context():
            self.assertNotEqual(Tip.query.filter_by(id=1).one().update, self.old_age)
            self.assertEqual(Tip.query.filter_by(id=2).one().update, self.old_age)
