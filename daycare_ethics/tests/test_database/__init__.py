# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""

"""

import unittest

import test_util, test_models

suite = unittest.TestSuite([
    unittest.TestLoader().loadTestsFromModule(test_util),
    unittest.TestLoader().loadTestsFromModule(test_models),
])

if __name__ == '__main__':
    unittest.main()
