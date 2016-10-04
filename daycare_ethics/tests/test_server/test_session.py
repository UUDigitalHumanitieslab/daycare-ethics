# (c) 2014, 2015, 2016 Digital Humanities Lab, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from unittest import TestCase

from ..common_fixtures import BaseFixture
from ...server.session import *
from ...database.models import Session


class BasicsTestCase(TestCase):
    def test_generate_key(self):
        keys = [generate_key() for i in range(10)]
        
        # probabilistic test: this one may fail at most once during your 
        # lifetime (p = 7.6e-53).
        self.assertEqual(len(set(keys)), 10)
        
        for k in keys:
            self.assertRegexpMatches(k, '[a-zA-Z0-9]{30}')
            self.assertEqual(len(k), KEY_LENGTH)


class SessionInterfaceTestCase(BaseFixture):
    def setUp(self):
        super(SessionInterfaceTestCase, self).setUp()
        self.cookie_name = self.app.config['SESSION_COOKIE_NAME']
    
    def test_nomodify(self):
        # Run 1: start from scratch, no preexisting session
        with self.client.session_transaction():
            pass
        with self.request_context():
            sessions = Session.query.all()
        self.assertEqual(len(sessions), 1)
        token = sessions[0].token
        payload = sessions[0].payload
        
        # Run 2: send the same token, explicitly
        with self.client.session_transaction(data={'t': token}):
            pass
        with self.request_context():
            sessions = Session.query.all()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].token, token)
        self.assertEqual(sessions[0].payload, payload)
        
        # Run 3: send the same token, by cookie
        with self.client.session_transaction(headers={
            'Cookie': '{}={};'.format(self.cookie_name, token),
        }):
            pass
        with self.request_context():
            sessions = Session.query.all()
        self.assertEqual(len(sessions), 1)
        self.assertEqual(sessions[0].token, token)
        self.assertEqual(sessions[0].payload, payload)
        
        # Run 4: send a faux token, explicitly
        faux_token = ''.join(reversed(token))
        with self.client.session_transaction(data={'t': faux_token}) as s:
            self.assertEqual(s['token'], faux_token)
            self.assertTrue(s['tainted'])
            self.assertTrue(s.permanent)
        with self.request_context():
            sessions = Session.query.all()
            sacred_session = Session.query.get(token)
            corrupted_session = Session.query.get(faux_token)
        self.assertEqual(len(sessions), 2)
        self.assertIsNotNone(sacred_session)
        self.assertIsNotNone(corrupted_session)
        self.assertEqual(sacred_session.payload, payload)
        self.assertTrue('tainted' in corrupted_session.payload)
        self.assertTrue(corrupted_session.payload['tainted'])
