# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

from flask import current_app
from flask.ext.admin import form
from flask.ext.admin.contrib.sqla import ModelView

from ..database.models import *


class MediaView(ModelView):
    column_list = ('name',)
    column_default_sort = ('id', True)
    form_columns = ('name', 'path')
    form_overrides = {
        'path': form.FileUploadField,
    }
    form_args = {
        'path': {
            'label': 'File',
            'base_path': lambda: current_app.instance_path,
            'allowed_extensions': ('mp4', 'jpg', 'jpeg', 'png'),
        }
    }

    def on_model_change(self, form, model, is_created=True):
        model.mime_type = form.path.data.headers['Content-Type']

    def __init__(self, session, name='Media', **kwargs):
        super(MediaView, self).__init__(Picture, session, name, **kwargs)


class CasesView(ModelView):
    column_list = ('title', 'publication', 'closure', 'yes_votes', 'no_votes')
    column_labels = {
        'yes_votes': 'Yes',
        'no_votes': 'No',
    }
    column_descriptions = {
        'publication': 'Date when the case goes live.',
        'closure': 'Date when the case is archived.',
    }
    column_default_sort = ('publication', True)
    form_columns = ('title', 'publication', 'closure', 'picture', 'text', 'proposition')

    def __init__(self, session, name='Cases', **kwargs):
        super(CasesView, self).__init__(Case, session, name, **kwargs)


class VotesView(ModelView):
    can_create = False
    can_delete = False
    can_edit = False
    column_sortable_list = (('case', 'case.title'), 'submission', 'agree')
    column_default_sort = ('submission', True)
    column_filters = ('case', 'submission')
    page_size = 100

    def __init__(self, session, name='Votes', **kwargs):
        super(VotesView, self).__init__(Vote, session, name, **kwargs)
