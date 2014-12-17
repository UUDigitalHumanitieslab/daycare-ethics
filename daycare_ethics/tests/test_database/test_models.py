# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""

"""

from unittest import TestCase

from ...database.models import *

class SQLADeclaredAttrTestCase (TestCase):
    def test_picture_refs (self):
        self.assertIn('picture', Case.__dict__)
        self.assertIn('picture', BrainTeaser.__dict__)

    def test_picture_backrefs (self):
        self.assertIn('cases', Picture.__dict__)
        self.assertIn('brain_teasers', Picture.__dict__)
