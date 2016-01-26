# (c) 2014, 2015 Digital Humanities Lab, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Runs all the tests in the suite.

    Code coverage is close to 100%. Only a few relatively simple bits
    are untested.
"""

import unittest

from daycare_ethics.tests import suite

if __name__ == '__main__':
    unittest.TextTestRunner().run(suite)
