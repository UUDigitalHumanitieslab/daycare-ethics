# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

"""
    Utilites specific to the database subpackage.
"""

import flask.ext.sqlalchemy as fsqla

def TableArgsMeta(parent_class, table_args):
    """
        Metaclass generator to set global defaults for __table_args__.
        
        See
        http://stackoverflow.com/questions/25770701/how-to-tell-sqlalchemy-once-that-i-want-innodb-for-the-entire-database
        for an explanation.
    """

    class _TableArgsMeta(parent_class):

        def __init__(cls, name, bases, dict_):
            if (    # Do not extend base class
                    '_decl_class_registry' not in cls.__dict__ and 
                    # Missing __tablename_ or equal to None means single table
                    # inheritance -- no table for it (columns go to table of
                    # base class)
                    cls.__dict__.get('__tablename__') and
                    # Abstract class -- no table for it (columns go to table[s]
                    # of subclass[es]
                    not cls.__dict__.get('__abstract__', False)):
                ta = getattr(cls, '__table_args__', {})
                if isinstance(ta, dict):
                    ta = dict(table_args, **ta)
                    cls.__table_args__ = ta
                else:
                    assert isinstance(ta, tuple)
                    if ta and isinstance(ta[-1], dict):
                        tad = dict(table_args, **ta[-1])
                        ta = ta[:-1]
                    else:
                        tad = dict(table_args)
                    cls.__table_args__ = ta + (tad,)
            super(_TableArgsMeta, cls).__init__(name, bases, dict_)

    return _TableArgsMeta

class InnoDBSQLAlchemy (fsqla.SQLAlchemy):
    """ Subclass in order to enable TableArgsMeta. """
    def make_declarative_base(self):
        """Creates the declarative base."""
        base = fsqla.declarative_base(
            cls = fsqla.Model,
            name = 'Model',
            metaclass = TableArgsMeta(
                fsqla._BoundDeclarativeMeta,
                {'mysql_engine': 'InnoDB'} ) )
        base.query = fsqla._QueryProperty(self)
        return base
