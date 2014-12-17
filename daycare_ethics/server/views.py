# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Directly visitable routes on the domain.
"""

from flask import send_from_directory

from . import public


@public.route('/')
def index():
    return send_from_directory(public.static_folder, 'index.html')
