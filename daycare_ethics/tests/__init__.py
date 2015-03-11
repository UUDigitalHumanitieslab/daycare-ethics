# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Top-level test suite to rule them all.
"""

import unittest

import test_server, test_database, test_admin, test_util

suite = unittest.TestSuite([
    test_server.suite,
    test_database.suite,
    test_admin.suite,
    unittest.TestLoader().loadTestsFromModule(test_util),
])

if __name__ == '__main__':
    unittest.main()
