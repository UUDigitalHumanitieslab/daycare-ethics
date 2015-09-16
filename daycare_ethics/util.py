# (c) 2014, 2015 Digital Humanities Lab, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

import os.path as op


TARGET_WIDTHS = 300, 424, 600, 848


def image_variants(fname):
    name = op.splitext(fname)[0]
    pattern = name + '_{}.jpeg'
    return [pattern.format(w) for w in TARGET_WIDTHS]
