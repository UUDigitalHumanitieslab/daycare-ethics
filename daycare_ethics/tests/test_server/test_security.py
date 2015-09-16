# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl
# Credits: Jeremy Allen helped to fix issues. (http://stackoverflow.com/a/32597959/1166087)

from datetime import datetime, timedelta

from flask import json, session

from ..common_fixtures import BaseFixture
from ...server.security import *


class BasicsTestCase (BaseFixture):
    def test_init_app(self):
        self.assertItemsEqual(self.app.captcha_data, [
            set(u'red orange yellow green blue purple pink grey'.split()),
            set(u'one two three four five six seven eight nine ten eleven'.split()),
            set(u'Paris London Berlin Madrid Amsterdam Dublin Stockholm Utrecht'.split()),
        ])
    
    def test_init_captcha(self):
        with self.request_context():
            now = datetime.today()
            captcha = init_captcha()
            challenge = set(captcha['captcha_challenge'].lower().split())
            answer = set(session['captcha-answer'])
            fillers = challenge - answer
            expiry = session['captcha-expires']
            self.assertTrue(answer < challenge)
            self.assertEqual(len(answer), ODDBALLS)
            self.assertEqual(len(fillers), NORMALS)
            answerpool, fillerpool = None, None
            for pool in self.app.captcha_data:
                lowerpool = set(map(lambda s: s.lower(), pool))
                if answer < lowerpool:
                    answerpool = pool
                if fillers < lowerpool:
                    fillerpool = pool
            self.assertIsNotNone(answerpool)
            self.assertIsNotNone(fillerpool)
            self.assertNotEqual(answerpool, fillerpool)
            self.assertEqual(str(expiry), captcha['captcha_expires'])
            timegap = expiry - now - AUTHENTICATION_TIME
            self.assertGreaterEqual(timegap, timedelta(seconds=0))
            self.assertLessEqual(timegap, timedelta(seconds=1))
            
            # It should also remove the captcha-quarantine field from the
            # session if there is one, but I have not found a way to test this
            # yet. The code below does not work.
            
            # with self.client.session_transaction() as s:
            #     s['captcha-quarantine'] = now + timedelta(minutes=30)
            # self.assertIn('captcha-quarantine', session)
            # init_captcha()
            # self.assertNotIn('captcha-quarantine', session)


class AuthorizeCaptchaTestCase (BaseFixture):
    def setUp(self):
        super(AuthorizeCaptchaTestCase, self).setUp()
        self.token = '1234567'
        with self.client as c:
            with c.session_transaction() as s:
                s['token'] = self.token
                s['captcha-expires'] = datetime.today() + timedelta(minutes=10)
                s['captcha-answer'] = u'one two three'.split()
        @self.app.route('/test', methods=['POST'])
        def testview():
            return '', 200 if authorize_captcha() else 400
    
    def test_authorize_captcha_unanswered(self):
        self.assertEqual(self.client.post('/test', data={
            't': self.token,
        }).status_code, 400)
    
    def test_authorize_captcha_expired(self):
        with self.client as c:
            with c.session_transaction(method='POST', data={
                't': self.token,
            }) as s:
                s['captcha-expires'] = datetime.today() - timedelta(minutes=1)
            self.assertEqual(c.post('/test', data={
                't': self.token,
                'ca': 'one two three',
            }).status_code, 400)
    
    def test_authorize_captcha_validation(self):
        response1 = self.client.post('/test', data={
            'ca': 'one two three',
            't': self.token,
        })
        self.assertEqual(response1.status_code, 200)
        self.assertEqual(self.client.post('/test', data={
            'ca': 'one two four',
            't': self.token,
        }).status_code, 400)


class CaptchaSafeTestCase (BaseFixture):
    def setUp(self):
        super(CaptchaSafeTestCase, self).setUp()
        self.token = '1234567'
        with self.client as c:
            with c.session_transaction() as s:
                s['token'] = self.token
                s['captcha-expires'] = datetime.today() + timedelta(minutes=10)
                s['captcha-answer'] = u'one two three'.split()
        @self.app.route('/test', methods=['POST'])
        def testview():
            return '', 200 if captcha_safe() else 400
    
    def test_captcha_safe_authorized(self):
        with self.client as c:
            self.assertEqual(c.post('/test', data={
                'ca': 'one two three',
                't': self.token,
            }).status_code, 200)
            self.assertEqual(len(session), 1)
    
    def test_captcha_safe_unauthorized(self):
        with self.client as c:
            now = datetime.today()
            self.assertEqual(c.post('/test', data={
                't': self.token,
            }).status_code, 400)
            self.assertEqual(len(session), 3)
            self.assertIn('captcha-quarantine', session)
            self.assertTrue(session.permanent)
            timegap = session['captcha-quarantine'] - now - QUARANTINE_TIME
            self.assertGreaterEqual(timegap, timedelta(seconds=0))
            self.assertLessEqual(timegap, timedelta(seconds=1))
    
    def test_captcha_safe_inquarantine(self):
        with self.client as c:
            quarantine = datetime.today().replace(microsecond=0) + QUARANTINE_TIME
            with c.session_transaction(method='POST', data={
                't': self.token,
            }) as s:
                s.clear()
                s['token'] = self.token
                s['captcha-quarantine'] = quarantine
            self.assertEqual(c.post('/test', data={
                't': self.token,
            }).status_code, 400)
            self.assertIn('captcha-quarantine', session)
            self.assertEqual(session['captcha-quarantine'], quarantine)
    
    def test_captcha_safe_outofquarantine(self):
        with self.client as c:
            quarantine = datetime.today().replace(microsecond=0) - timedelta(minutes=10)
            with c.session_transaction(method='POST', data={
                't': self.token,
            }) as s:
                s.clear()
                s['token'] = self.token
                s['captcha-quarantine'] = quarantine
            self.assertEqual(c.post('/test', data={
                't': self.token,
            }).status_code, 200)
            self.assertNotIn('captcha-quarantine', session)
    
    def test_captcha_safe_default(self):
        with self.client as c:
            with c.session_transaction(method='POST', data={
                't': self.token,
            }) as s:
                s.clear()
                s['token'] = self.token
            self.assertEqual(c.post('/test', data={
                't': self.token,
            }).status_code, 200)


class VerifyNaturalTestCase (BaseFixture):
    def setUp(self):
        super(VerifyNaturalTestCase, self).setUp()
        @self.app.route('/test', methods=['POST'])
        def testview():
            verify_natural()
            return '', 200
    
    def test_verify_natural(self):
        token = '1234567'
        with self.client as c:
            with c.session_transaction() as s:
                s['token'] = token
            for flags in range(8):  # lo2hi: user agent, referer, tainted
                headerfields = {}
                with c.session_transaction(method='POST', data={
                    't': token,
                }) as s:
                    s.clear()
                    s['token'] = token
                if flags & 1:
                    headerfields['User-Agent'] = 'Flask test client'
                if flags & 2:
                    headerfields['Referer'] = 'unittest'
                if flags & 4:
                    with c.session_transaction(method='POST', data={
                        't': token,
                    }) as s:
                        s['tainted'] = True
                status = c.post('/test', headers=headerfields, data={
                    't': token,
                }).status_code
                tainted = 'tainted' in session
                if flags == 3:
                    self.assertFalse(tainted)
                    self.assertEqual(status, 200)
                else:
                    self.assertTrue(tainted)
                    self.assertEqual(status, 400)


class TokenizeResponseTestCase (BaseFixture):
    def setUp(self):
        super(TokenizeResponseTestCase, self).setUp()
        self.now = datetime.today()
    
    def test_tokenize_response_dict(self):
        with self.request_context():
            payload = {u'status': u'success'}
            result = tokenize_response(payload, self.now)
            self.assertIn('token', session)
            self.assertIn('last-request', session)
            self.assertEqual(session['last-request'], self.now)
            self.assertIn('json', result.mimetype)
            content = json.loads(result.get_data())
            self.assertIn('token', content)
            self.assertEqual(content['token'], session['token'])
            del content['token']
            self.assertEqual(content, payload)
            self.assertEqual(result.status_code, 200)
            self.assertEqual(len(result.headers), 2)  # Content-Type and -Length
    
    def test_tokenize_response_singleton(self):
        with self.request_context():
            payload = {u'status': u'success'},
            result = tokenize_response(payload, self.now)
            self.assertIn('token', session)
            self.assertIn('last-request', session)
            self.assertEqual(session['last-request'], self.now)
            self.assertIn('json', result.mimetype)
            content = json.loads(result.get_data())
            self.assertIn('token', content)
            self.assertEqual(content['token'], session['token'])
            del content['token']
            self.assertEqual(content, payload[0])
            self.assertEqual(result.status_code, 200)
            self.assertEqual(len(result.headers), 2)  # Content-Type and -Length
    
    def test_tokenize_response_pair(self):
        with self.request_context():
            payload = {u'status': u'success'}, 300
            result = tokenize_response(payload, self.now)
            self.assertIn('token', session)
            self.assertIn('last-request', session)
            self.assertEqual(session['last-request'], self.now)
            self.assertIn('json', result[0].mimetype)
            content = json.loads(result[0].get_data())
            self.assertIn('token', content)
            self.assertEqual(content['token'], session['token'])
            del content['token']
            self.assertEqual(content, payload[0])
            self.assertEqual(result[1], 300)
            self.assertEqual(len(result[0].headers), 2)  # Content-Type and -Length
    
    def test_tokenize_response_triplet(self):
        with self.request_context():
            payload = {u'status': u'success'}, 300, {'test': 'test'}
            result = tokenize_response(payload, self.now)
            self.assertIn('token', session)
            self.assertIn('last-request', session)
            self.assertEqual(session['last-request'], self.now)
            self.assertIn('json', result[0].mimetype)
            content = json.loads(result[0].get_data())
            self.assertIn('token', content)
            self.assertEqual(content['token'], session['token'])
            del content['token']
            self.assertEqual(content, payload[0])
            self.assertEqual(result[1], 300)
            self.assertEqual(len(result[0].headers), 2)  # Content-Type and -Length
            self.assertEqual(result[2], payload[2])


class SessionEnableTestCase (BaseFixture):
    def setUp(self):
        super(SessionEnableTestCase, self).setUp()
        @self.app.route('/test', methods=['POST'])
        @session_enable
        def testview():
            return {'status': 'success'}
    
    def test_session_enable(self):
        with self.client as c:
            result = c.post('/test')
            self.assertEqual(result.status_code, 200)
            self.assertIn('json', result.mimetype)
            content = json.loads(result.get_data())
            self.assertIn('token', content)
            self.assertIn('token', session)
            self.assertEqual(content['token'], session['token'])


class SessionProtectTestCase (BaseFixture):
    def setUp(self):
        super(SessionProtectTestCase, self).setUp()
        @self.app.route('/test', methods=['POST'])
        @session_protect
        def testview():
            return {'status': 'success'}
    
    def prepare(self):
        with self.client as c:
            with c.session_transaction() as s:
                s['token'] = 'qwertyuiop'
                s['last-request'] = datetime.today() - timedelta(seconds=1)
    
    def test_session_protect_new(self):
        with self.client as c:
            self.assertEqual(c.post('/test', data={
                't': 'qwertyuiop',
            }, headers={
                'User-Agent': 'Flask test client',
                'Referer': 'unittest',
            }).status_code, 400)
            self.assertIn('tainted', session)
    
    def test_session_protect_authentication(self):
        self.prepare()
        with self.client as c:
            self.assertEqual(c.post('/test', data={
                't': 'qwertyuiop',
            }).status_code, 400)
            self.assertIn('tainted', session)
    
    def test_session_protect_completion(self):
        self.prepare()
        with self.client as c:
            self.assertEqual(c.post('/test', headers={
                'User-Agent': 'Flask test client',
                'Referer': 'unittest',
            }).status_code, 400)
            self.assertIn('tainted', session)
    
    def test_session_protect_comparison(self):
        self.prepare()
        with self.client as c:
            self.assertEqual(c.post('/test', data={
                't': 'qwertyuio',
            }, headers={
                'User-Agent': 'Flask test client',
                'Referer': 'unittest',
            }).status_code, 400)
            self.assertIn('tainted', session)
    
    def test_session_protect_delay(self):
        self.prepare()
        with self.client as c:
            with c.session_transaction(method='POST', data={
                't': 'qwertyuiop',
            }) as s:
                s['last-request'] = datetime.today() + timedelta(seconds=1)
            self.assertEqual(c.post('/test', data={
                't': 'qwertyuiop',
            }, headers={
                'User-Agent': 'Flask test client',
                'Referer': 'unittest',
            }).status_code, 400)
            self.assertIn('tainted', session)
    
    def test_session_protect_tokenization(self):
        self.prepare()
        with self.client as c:
            result = c.post('/test', data={
                't': 'qwertyuiop',
            }, headers={
                'User-Agent': 'Flask test client',
                'Referer': 'unittest',
            })
            self.assertEqual(result.status_code, 200)
            self.assertIn('json', result.mimetype)
            content = json.loads(result.get_data())
            self.assertIn('token', content)
            self.assertIn('token', session)
            self.assertEqual(content['token'], session['token'])
