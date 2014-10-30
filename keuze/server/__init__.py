# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""

"""

import flask

public = flask.Blueprint(
    'public',
    __name__,
    static_folder = '../www',
    static_url_path = ''        )
