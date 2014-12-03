# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""

"""

import unittest

from ..common_fixtures import BaseFixture

class ViewsTestCase (BaseFixture):
    def test_index(self):
        response = self.app.get('/')
        self.assertIn(
            '<script type="text/javascript" src="js/index.js"></script>',
            response.data   )

if __name__ == '__main__':
    unittest.main()