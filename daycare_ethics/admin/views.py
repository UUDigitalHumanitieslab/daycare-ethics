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
