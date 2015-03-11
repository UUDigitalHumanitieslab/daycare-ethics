# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from unittest import TestCase

from ..util import *


class ImageVariantTestCase(TestCase):
    def test_image_variants(self):
        variants = image_variants('testimage.png')
        for width, variant in zip(TARGET_WIDTHS, variants):
            self.assertEqual('testimage_{}.jpeg'.format(width), variant)

