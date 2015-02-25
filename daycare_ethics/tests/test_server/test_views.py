# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from datetime import datetime

from ..common_fixtures import BaseFixture
from ...database.models import *
from ...database.db import db


class IndexTestCase (BaseFixture):
    def test_index(self):
        response = self.client.get('/')
        self.assertIn(
            '<script src="js/index.js"></script>',
            response.data   )
        self.assertEqual(response.status_code, 200)

    def test_index_cached(self):
        now = datetime.today()
        next_ = now.replace(hour=now.hour + 1)
        response = self.client.get('/', headers={
            'If-Modified-Since': next_.strftime('%a, %d %b %Y %H:%M:%S %z%Z'),
        })
        self.assertEqual(response.status_code, 304)


class CasusTestCase (BaseFixture):
    def setUp (self):
        super(CasusTestCase, self).setUp()
        casus1 = Case(title='casus1')
        casus2 = Case(title='casus2')
        casus3 = Case(title='casus3')
        now = datetime.today()
        next_ = now.replace(hour=now.hour - 1)
        def next_date():
            next_ = next_.replace(second=next_.second + 1)
            return next_
        ses = db.session
        with self.request_context():
            for count in range(30):
                ses.add(Vote(case=casus1, submission=next_date(), agree=(count % 4)))
            for count in range(40):
                ses.add(Vote(case=casus2, submission=next_date(), agree=(count % 3)))
            for count in range(50):
                ses.add(Vote(case=casus3, submission=next_date(), agree=not(count % 4)))
            ses.commit()
    