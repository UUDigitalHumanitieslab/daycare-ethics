# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from datetime import datetime, timedelta

from flask import json

from ..common_fixtures import BaseFixture
from ...database.models import *
from ...database.db import db
from ...server.views import *


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
        casus4 = Case(title='casus4', publication=now + timedelta(weeks=1))
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
            ses.add(casus4)
            ses.commit()
    
    def test_current_casus_redirect(self):
        response = self.client.get('/case')
        self.assertEqual(response.status_code, 301)
    
    def test_current_casus(self):
        response = self.client.get('/case/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('json', response.mimetype)
        response_object = json.loads(response.data)
        self.assertEqual(response_object['title'], 'casus3')
        self.assertLessEqual(response_object['publication'], datetime.today().isoformat())
        
    def test_retrieve_casus(self):
        response1 = self.client.get('/case/1')
        self.assertEqual(response1.status_code, 200)
        self.assertIn('json', response1.mimetype)
        response1_object = json.loads(response1.data)
        self.assertEqual(response1_object['title'], 'casus1')
        response4 = self.client.get('/case/4')
        self.assertEqual(response4.status_code, 404)
        response5 = self.client.get('/case/5')
        self.assertEqual(response5.status_code, 404)

    def test_casus2dict(self):
        with self.request_context():
            testcase = Case.query.get(2)
        testdict = casus2dict(testcase)
        self.assertEqual(testdict['title'], testcase.title)
        self.assertEqual(testdict['publication'], str(testcase.publication))
        self.assertEqual(testdict['week'], testcase.publication.isocalendar()[1])
        self.assertIsNone(testdict['closure'])

    def test_available_casus(self):
        with self.request_context():
            testoutput = available_casus().all()
            testreference = [
                Case.query.get(3),
                Case.query.get(2),
                Case.query.get(1),
            ]
        self.assertEqual(len(testoutput), 3)
        for output, reference in zip(testoutput, testreference):
            self.assertIs(output, reference)

    def test_casus_archive(self):
        response = self.client.get('/case/archive')
        self.assertEqual(response.status_code, 200)
        self.assertIn('json', response.mimetype)
        response_object = json.loads(response.data)
        with self.request_context():
            reference_dict = map(casus2dict, available_casus().all())
        self.assertEqual(response_object['all'], reference_dict)

    def test_vote_casus_protection(self):
        with self.client as c:
            response1 = c.post('/case/vote', data={
                'id': 3,
                'choice': 'yes',
            })
            self.assertTrue(session['tainted'])
        self.assertEqual(response1.status_code, 400)

    def test_vote_casus_passthrough(self):
        """ Warning: this is not a full coverage test.
        
        All differences that you find between the session and the request 
        in this test and test_vote_casus_protection are necessary 
        conditions for vote_casus to succeed (pass through). For full 
        coverage, you would have to selectively omit each of those 
        differences independently; in each case, the response should have 
        status code 400 (though with different response data).
        """
        with self.client as c:
            token = 'abcdef'
            with c.session_transaction() as s:
                s['token'] = token
                s['last-request'] = datetime.now() - timedelta(hours=1)
            response2 = c.post('/case/vote', data={
                'id': 3,
                'choice': 'yes',
                't': token,
            }, headers={
                'User-Agent': 'Flask test client',
                'Referer': 'unittest',
                'X-Requested-With': 'XMLHttpRequest',
            })
            self.assertEqual(response2.status_code, 200)
            self.assertIn('json', response2.mimetype)
            response_data = json.loads(response2.data)
            self.assertEqual(response_data['status'], 'success')
            self.assertEqual(response_data['token'], session['token'])
        with self.request_context():
            self.assertEqual(Case.query.get(3).yes_votes, 1)
