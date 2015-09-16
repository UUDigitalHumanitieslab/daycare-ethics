#!/usr/bin/env python

# (c) 2014, 2015 Digital Humanities Lab, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Run a local test server with the serverside application.
"""

from sys import argv

from daycare_ethics import create_app


class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


if __name__ == '__main__':
    if len(argv) >= 2:
        app = create_app(config_file=argv[1])
    else:
        app = create_app(config_obj=Config)
    app.debug = True
    app.run()
