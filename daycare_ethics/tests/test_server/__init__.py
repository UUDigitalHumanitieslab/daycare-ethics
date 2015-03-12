# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Combined test suite for the modules of the server package.
"""

import unittest

import test_views, test_util

suite = unittest.TestSuite([
    unittest.TestLoader().loadTestsFromModule(test_views),
])

if __name__ == '__main__':
    unittest.main()
