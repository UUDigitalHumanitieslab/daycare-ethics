# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""

"""

import unittest

import test_server
import test_database

suite = unittest.TestSuite([
    test_server.suite,
    test_database.suite,
])

if __name__ == '__main__':
    unittest.main()
