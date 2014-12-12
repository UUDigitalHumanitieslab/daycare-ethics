# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""

"""

import unittest

import test_views

suite = unittest.TestSuite([unittest.TestLoader().loadTestsFromModule(test_views)])

if __name__ == '__main__':
    unittest.main()