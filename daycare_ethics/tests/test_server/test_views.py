# (c) 2014, 2015 Digital Humanities Lab, Utrecht University
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

class ReflectionTestCase (BaseFixture):
    def setUp(self):
        super(ReflectionTestCase, self).setUp()
        now = datetime.today()
        reflection1 = BrainTeaser(title='reflection1', publication=now - timedelta(weeks=3))
        reflection2 = BrainTeaser(title='reflection2', publication=now - timedelta(weeks=2))
        reflection3 = BrainTeaser(title='reflection3', publication=now - timedelta(weeks=1))
        reflection4 = BrainTeaser(title='reflection4', publication=now + timedelta(weeks=1))
        second = timedelta(seconds=1)
        def next_date():
            next_date.state += second
            return next_date.state
        next_date.state = now - timedelta(hours=1)
        reflections = [reflection1, reflection2, reflection3, reflection4]
        ses = db.session
        with self.request_context():
            for count, reflection in enumerate(reflections * 2):
                ses.add(Response(
                    submission=next_date(),
                    pseudonym='test' + str(count % 3),
                    message='banana' * count,
                    brain_teaser=reflection
                ))
            ses.add(reflection4)
            ses.commit()
    
    def test_current_reflection_redirect(self):
        response = self.client.get('/reflection')
        self.assertEqual(response.status_code, 301)
    
    def test_current_reflection(self):
        response = self.client.get('/reflection/', headers={
            'User-Agent': 'Flask test client',
            'Referer': 'unittest',
            'X-Requested-With': 'XMLHttpRequest',
        })
        self.assertEqual(response.status_code, 200)
        self.assertIn('json', response.mimetype)
        response_object = json.loads(response.data)
        self.assertEqual(response_object['title'], 'reflection3')
        self.assertLessEqual(response_object['publication'], datetime.today().isoformat())
        
    def test_retrieve_reflection(self):
        response1 = self.client.get('/reflection/1/')
        self.assertEqual(response1.status_code, 200)
        self.assertIn('json', response1.mimetype)
        response1_object = json.loads(response1.data)
        self.assertEqual(response1_object['title'], 'reflection1')
        response4 = self.client.get('/reflection/4/')
        self.assertEqual(response4.status_code, 404)
        response5 = self.client.get('/reflection/5/')
        self.assertEqual(response5.status_code, 404)

    def test_reflection2dict(self):
        with self.request_context():
            testreflection = BrainTeaser.query.get(2)
            testdict = reflection2dict(testreflection, True)
        self.assertEqual(testdict['title'], testreflection.title)
        self.assertEqual(testdict['publication'], str(testreflection.publication))
        self.assertEqual(testdict['week'], testreflection.publication.isocalendar()[1])
        self.assertIsNone(testdict['closure'])
        with self.request_context():
            self.assertEqual(testdict['responses'], reflection_replies(2))

    def test_available_reflection(self):
        with self.request_context():
            testoutput = available_reflection().all()
            testreference = [
                BrainTeaser.query.get(3),
                BrainTeaser.query.get(2),
                BrainTeaser.query.get(1),
            ]
        self.assertEqual(len(testoutput), 3)
        for output, reference in zip(testoutput, testreference):
            self.assertIs(output, reference)

    def test_response2dict(self):
        with self.request_context():
            response3 = Response.query.get(3)
        output = response2dict(response3)
        self.assertEqual(response3.id, output['id'])
        self.assertEqual(str(response3.submission.date()), output['submission'])
        self.assertEqual(response3.pseudonym, output['pseudonym'])
        self.assertEqual(response3.message, output['message'])
        self.assertEqual(response3.upvotes, output['up'])
        self.assertEqual(response3.downvotes, output['down'])

    def test_reflection_replies(self):
        with self.request_context():
            output1 = reflection_replies(1)
            output2 = reflection_replies(1, Response.query.get(2).submission)
        self.assertListEqual(output1[1:], output2)
        self.assertEqual(output1[0]['id'], 1)
        self.assertEqual(output1[1]['id'], 5)

    def test_reflection_archive(self):
        response = self.client.get('/reflection/archive')
        self.assertEqual(response.status_code, 200)
        self.assertIn('json', response.mimetype)
        response_object = json.loads(response.data)
        with self.request_context():
            reference_list = map(reflection2dict, available_reflection().all())
        for result, reference in zip(response_object['all'], reference_list):
            self.assertEqual(result['id'], reference['id'])
            self.assertEqual(result['title'], reference['title'])
            self.assertEqual(result['publication'], reference['publication'])
            self.assertEqual(result['week'], reference['week'])
            self.assertEqual(result['closure'], reference['closure'])
            self.assertEqual(result['text'], reference['text'])
            self.assertEqual(result['responses'], reference['responses'])

    def test_reply_to_reflection_protection(self):
        with self.client as c:
            response1 = c.post('/reflection/3/reply', data={
                'p': 'test4',
                'r': 'testmessage',
            })
            self.assertTrue(session['tainted'])
        self.assertEqual(response1.status_code, 400)

    def test_reply_to_reflection_passthrough(self):
        """ Warning: this is not a full coverage test.

        All differences that you find between the session and the request
        in this test and test_reply_to_reflection_protection are necessary
        conditions for reply_to_reflection to succeed (pass through), and 
        then some. For full coverage, you would have to selectively omit 
        each of those differences independently; in each reflection, the 
        response should have status code 400 (though with different 
        response data).
        """
        with self.client as c:
            token = 'abcdef'
            with c.session_transaction() as s:
                s['token'] = token
                s['last-request'] = datetime.now() - timedelta(hours=1)
            
            response2 = c.post('/reflection/3/reply', data={
                'p': 'test4',
                'r': 'testmessage',
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
            
            with c.session_transaction() as s:
                s['token'] = token
                s['last-request'] = datetime.now() - timedelta(milliseconds=201)
            
            response3 = c.post('/reflection/3/reply', data={
                'p': 'test4',
                'r': 'testmessage',
                't': token,
            }, headers={
                'User-Agent': 'Flask test client',
                'Referer': 'unittest',
                'X-Requested-With': 'XMLHttpRequest',
            })
            self.assertEqual(response3.status_code, 200)
            self.assertIn('json', response3.mimetype)
            response_data = json.loads(response3.data)
            self.assertEqual(response_data['status'], 'captcha')
            self.assertEqual(response_data['token'], session['token'])
            
            answer = ' '.join(session['captcha-answer'])
            with c.session_transaction() as s:
                s['token'] = token
                s['last-request'] = datetime.now() - timedelta(milliseconds=201)
            
            response4 = c.post('/reflection/3/reply', data={
                'p': 'test4',
                'r': 'testmessage',
                't': token,
                'ca': answer,
            }, headers={
                'User-Agent': 'Flask test client',
                'Referer': 'unittest',
                'X-Requested-With': 'XMLHttpRequest',
            })
            self.assertEqual(response4.status_code, 200)
            self.assertIn('json', response4.mimetype)
            response_data = json.loads(response4.data)
            self.assertEqual(response_data['status'], 'success')
            self.assertEqual(response_data['token'], session['token'])
            
            with c.session_transaction() as s:
                s['token'] = token
                s['last-request'] = datetime.now() - timedelta(milliseconds=201)
            
            response5 = c.post('/reflection/3/reply', data={
                'p': 'test4',
                'r': 'testmessage',
                't': token,
                'last-retrieve': datetime.today() - timedelta(days=1),
            }, headers={
                'User-Agent': 'Flask test client',
                'Referer': 'unittest',
                'X-Requested-With': 'XMLHttpRequest',
            })
            self.assertEqual(response5.status_code, 200)
            self.assertIn('json', response5.mimetype)
            response_data = json.loads(response5.data)
            self.assertEqual(response_data['status'], 'ninja')
            self.assertEqual(len(response_data['new']), 4)
            self.assertGreaterEqual(response_data['since'], str(datetime.today() - timedelta(seconds=2)))
            self.assertEqual(response_data['token'], session['token'])

    def test_moderate_reply_protection(self):
        with self.client as c:
            response1 = c.post('/reply/3/moderate/', data={
                'choice': 'up',
            })
            self.assertTrue(session['tainted'])
        self.assertEqual(response1.status_code, 400)

    def test_moderate_reply_passthrough(self):
        """ Warning: this is not a full coverage test.

        All differences that you find between the session and the request
        in this test and test_moderate_reply_protection are necessary
        conditions for reply_to_reflection to succeed (pass through). For 
        full coverage, you would have to selectively omit each of those 
        differences independently; in each reflection, the response should 
        have status code 400 (though with different response data).
        """
        with self.client as c:
            token = 'abcdef'
            with c.session_transaction() as s:
                s['token'] = token
                s['last-request'] = datetime.now() - timedelta(hours=1)
            
            response2 = c.post('/reply/3/moderate/', data={
                'choice': 'up',
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
            
            reply = Response.query.get(3)
            self.assertEqual(reply.upvotes, 1)
            self.assertEqual(reply.downvotes, 0)

class TipsTestCase (BaseFixture):
    def setUp(self):
        super(TipsTestCase, self).setUp()
        now = datetime.today()
        ses = db.session
        with self.request_context():
            ses.add(Tip(
                create=now - timedelta(hours=6),
                update=now - timedelta(hours=5),
                what='labour code',
                title='test1'
            ))
            ses.add(Tip(
                create=now - timedelta(hours=5),
                update=now - timedelta(hours=4),
                what='labour code',
                title='test2'
            ))
            ses.add(Tip(
                create=now - timedelta(hours=4),
                update=now - timedelta(hours=3),
                what='book',
                title='test3'
            ))
            ses.add(Tip(
                create=now - timedelta(hours=3),
                update=now - timedelta(hours=2),
                what='book',
                title='test4'
            ))
            ses.add(Tip(
                create=now - timedelta(hours=2),
                update=now - timedelta(hours=1),
                what='site',
                title='test5'
            ))
            ses.add(Tip(
                create=now - timedelta(hours=1),
                update=now,
                what='site',
                title='test6'
            ))
            ses.commit()
    
    def test_tip2dict(self):
        with self.request_context():
            tip = Tip.query.get(1)
        output = tip2dict(tip)
        self.assertEqual(output['id'], tip.id)
        self.assertEqual(output['created'], str(tip.create))
        self.assertEqual(output['updated'], str(tip.update))
        self.assertEqual(output['author'], tip.author)
        self.assertEqual(output['title'], tip.title)
        self.assertEqual(output['text'], tip.text)
        self.assertEqual(output['href'], tip.href)
    
    def test_retrieve_tips(self):
        with self.client as c:
            response1 = c.get('/tips/')
            self.assertEqual(response1.status_code, 200)
            self.assertIn('json', response1.mimetype)
            response1_data = json.loads(response1.data)
            self.assertEqual(response1_data['labour'][0]['id'], 2)
            self.assertEqual(response1_data['labour'][1]['id'], 1)
            self.assertEqual(response1_data['book'][0]['id'], 4)
            self.assertEqual(response1_data['book'][1]['id'], 3)
            self.assertEqual(response1_data['site'][0]['id'], 6)
            self.assertEqual(response1_data['site'][1]['id'], 5)
            
            Tip.query.get(5).update = datetime.today()
            db.session.commit()
            response2 = c.get('/tips/')
            self.assertEqual(response2.status_code, 200)
            self.assertIn('json', response2.mimetype)
            response2_data = json.loads(response2.data)
            self.assertEqual(response2_data['labour'][0]['id'], 2)
            self.assertEqual(response2_data['labour'][1]['id'], 1)
            self.assertEqual(response2_data['book'][0]['id'], 4)
            self.assertEqual(response2_data['book'][1]['id'], 3)
            self.assertEqual(response2_data['site'][0]['id'], 5)
            self.assertEqual(response2_data['site'][1]['id'], 6)

