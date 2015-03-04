# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from datetime import datetime, timedelta

from flask import json

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
    def setUp(self):
        super(CasusTestCase, self).setUp()
        now = datetime.today()
        casus1 = Case(title='casus1', publication=now - timedelta(weeks=3))
        casus2 = Case(title='casus2', publication=now - timedelta(weeks=2))
        casus3 = Case(title='casus3', publication=now - timedelta(weeks=1))
        second = timedelta(seconds=1)
        def next_date():
            next_date.state += second
            return next_date.state
        next_date.state = now - timedelta(hours=1)
        ses = db.session
        with self.request_context():
            for count in range(30):
                ses.add(Vote(case=casus1, submission=next_date(), agree=True if (count % 4) else False))
            for count in range(40):
                ses.add(Vote(case=casus2, submission=next_date(), agree=True if (count % 3) else False))
            for count in range(50):
                ses.add(Vote(case=casus3, submission=next_date(), agree=False if (count % 4) else True))
            ses.commit()
    
    def test_current_casus_redirect(self):
        response = self.client.get('/case')
        self.assertEqual(response.status_code, 301)
    
    def test_current_casus(self):
        with self.request_context():
            casus3 = Case.query.order_by(Case.publication.desc()).first()
        response = self.client.get('/case/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('json', response.mimetype)
        response_object = json.loads(response.data)
        self.assertEqual(response_object['title'], 'casus3')
        self.assertEqual(response_object['publication'], casus3.publication.isoformat())
        