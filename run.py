#!/usr/bin/env python

# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""

"""

from keuze import create_app

class Config:
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

if __name__ == '__main__':
    app = create_app(config_obj=Config)
    app.debug = True
    app.run()
