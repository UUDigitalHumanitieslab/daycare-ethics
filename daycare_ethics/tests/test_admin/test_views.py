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

    def tearDown(self):
        db.drop_all(app=self.app)

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
