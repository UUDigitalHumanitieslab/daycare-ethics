# (c) 2014, 2015 Digital Humanities Lab, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Combined test suite for the modules of the server package.
"""

import unittest

import test_views, test_util, test_security

suite = unittest.TestSuite([
    unittest.TestLoader().loadTestsFromModule(test_views),
    unittest.TestLoader().loadTestsFromModule(test_security),
])

if __name__ == '__main__':
    unittest.main()
