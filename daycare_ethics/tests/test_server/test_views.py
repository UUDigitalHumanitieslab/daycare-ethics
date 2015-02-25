# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from datetime import datetime

from ..common_fixtures import BaseFixture


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
