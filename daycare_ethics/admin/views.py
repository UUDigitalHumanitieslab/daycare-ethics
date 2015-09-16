# (c) 2014, 2015 Digital Humanities Lab, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

import os.path as op
from datetime import datetime

from wtforms import validators, widgets
from flask import current_app, flash
from flask.ext.admin import form
from flask.ext.admin.actions import action, ActionsMixin
from flask.ext.admin.contrib.sqla import ModelView

from PIL import Image

from ..util import TARGET_WIDTHS, image_variants
from ..database.models import *
from .util import download_csv


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
        if model.mime_type.startswith('image'):
            model_path = op.join(current_app.instance_path, model.path)
            original = Image.open(model_path)
            for width, name in zip(TARGET_WIDTHS, image_variants(model_path)):
                im = original.copy()
                im.thumbnail((width, width), Image.LANCZOS)
                im.save(op.join(current_app.instance_path, name), quality=95)

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
        'closure': 'Date when voting becomes unavailable.',
    }
    column_default_sort = ('publication', True)
    form_columns = (
        'title',
        'publication',
        'closure',
        'picture',
        'text',
        'proposition',
        'background',
    )
    form_args = {
        'background': {
            'label': 'Background color',
            'validators': [
                validators.Regexp(r'^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$'),
            ],
        }
    }
    form_widget_args = {
        'background': {
            'placeholder': '#RRGGBB',
        }
    }

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

    @action('Export', 'Download as CSV')
    def export_data(self, ids):
        return download_csv(self, ids, 'votes')

    def __init__(self, session, name='Votes', **kwargs):
        super(VotesView, self).__init__(Vote, session, name, **kwargs)
        self.init_actions()


class BrainTeasersView(ModelView):
    column_list = ('title', 'publication', 'closure')
    column_descriptions = {
        'publication': 'Date when the reflection item goes live.',
        'closure': 'Date when the discussion will close.',
    }
    column_default_sort = ('publication', True)
    form_columns = ('title', 'publication', 'closure', 'text')

    def __init__(self, session, name='Brain teasers', **kwargs):
        super(BrainTeasersView, self).__init__(BrainTeaser, session, name, **kwargs)


class ResponsesView(ModelView, ActionsMixin):
    can_create = False
    can_edit = False
    column_sortable_list = (
        ('brain_teaser', 'brain_teaser.title'),
        'submission',
        'pseudonym',
        'upvotes',
        'downvotes',
    )
    column_default_sort = ('submission', True)
    column_searchable_list = ('pseudonym', 'message')
    column_filters = ('brain_teaser', 'submission', 'pseudonym', 'upvotes', 'downvotes')
    page_size = 100

    @action('Export', 'Download as CSV')
    def export_data(self, ids):
        return download_csv(self, ids, 'responses')

    def __init__(self, session, name='Responses', **kwargs):
        super(ResponsesView, self).__init__(Response, session, name, **kwargs)
        self.init_actions()


class TipsView(ModelView):
    column_list = ('what', 'author', 'title', 'update')
    column_labels = {'update': 'Last update'}
    form_columns = ('what', 'author', 'title', 'text', 'href')
    form_args = {
        'text': {
            'label': 'Description',
        },
        'href': {
            'label': 'Hyperlink',
            'validators': [validators.URL(),],
            'widget': widgets.TextInput(),
        },
    }
    page_size = 50

    def on_model_change(self, form, model, is_created=True):
        model.update = datetime.now()
        if is_created:
            model.create = model.update

    @action('Bump', 'Mark as updated')
    def bump(self, ids):
        now = datetime.now()
        count = Tip.query.filter(Tip.id.in_(ids)).update({Tip.update: now}, False)
        db.session.commit()
        flash('{} tips have been bumped.'.format(count))

    def __init__(self, session, name='Tips', **kwargs):
        super(TipsView, self).__init__(Tip, session, name, **kwargs)
