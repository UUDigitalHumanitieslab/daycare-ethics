# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

import StringIO
import csv

from flask import current_app, make_response
from flask.ext.admin import form
from flask.ext.admin.actions import action, ActionsMixin
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


class VotesView(ModelView, ActionsMixin):
    can_create = False
    can_delete = False
    can_edit = False
    column_sortable_list = (('case', 'case.title'), 'submission', 'agree')
    column_default_sort = ('submission', True)
    column_filters = ('case', 'submission')
    page_size = 100

    @action('Export', 'Export selected data to CSV')
    def export_data(self, ids):
        headers = [c[0] if type(c) == tuple else c for c in self.get_list_columns()]
        data = Vote.query.filter(Vote.id.in_(ids)).all()
        buffer = StringIO.StringIO(b'')
        writer = csv.writer(buffer, delimiter=';')
        writer.writerow(headers)
        for vote in data:
            writer.writerow((vote.case.title, vote.submission, vote.agree))
        response = make_response(buffer.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename="votes.csv"'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return response

    def __init__(self, session, name='Votes', **kwargs):
        super(VotesView, self).__init__(Vote, session, name, **kwargs)
        self.init_actions()
