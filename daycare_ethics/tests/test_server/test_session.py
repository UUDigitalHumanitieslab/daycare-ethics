# (c) 2014, 2015 Digital Humanities Lab, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from unittest import TestCase

from ...server.session import *


class BasicsTestCase (TestCase):
    def test_generate_key(self):
        keys = [generate_key() for i in range(10)]
        
        # probabilistic test: this one may fail at most once during your 
        # lifetime (p = 7.6e-53).
        self.assertEqual(len(set(keys)), 10)
        
        for k in keys:
            self.assertRegexpMatches(k, '[a-zA-Z0-9]{30}')
            self.assertEqual(len(k), KEY_LENGTH)

