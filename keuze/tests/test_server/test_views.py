# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""

"""

from datetime import datetime

from ..common_fixtures import BaseFixture

class ViewsTestCase (BaseFixture):
    def test_index(self):
        response = self.app.get('/')
        self.assertIn(
            '<script type="text/javascript" src="js/index.js"></script>',
            response.data   )
        self.assertEqual(response.status_code, 200)

    def test_index_cached(self):
        now = datetime.today()
        next = now.replace(hour = now.hour + 1)
        response = self.app.get('/', headers = {
            'If-Modified-Since': next.strftime('%a, %d %b %Y %H:%M:%S %z%Z'),
        })
        self.assertEqual(response.status_code, 304)
