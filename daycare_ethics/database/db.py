# (c) 2014, 2015 Digital Humanities Lab, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Database object for use throughout the Flask side of the project.
"""

import util

db = util.InnoDBSQLAlchemy()
