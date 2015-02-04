# (c) 2014 Digital Humanities Lab, Faculty of Humanities, Utrecht University
# Author: Julian Gonggrijp, j.gonggrijp@uu.nl

import StringIO
import csv
from datetime import datetime

from flask import request, make_response


def download_csv(self, ids, tablename):
    headers = [c[0] if type(c) == tuple else c for c in self.get_list_columns()]
    data = self.model.query.filter(self.model.id.in_(ids)).all()
    filename = '{}_{}_{}.csv'.format(
        tablename,
        datetime.utcnow().strftime('%y%m%d%H%M'),
        request.query_string )
    buffer = StringIO.StringIO(b'')
    writer = csv.writer(buffer, delimiter=';')
    writer.writerow(headers)
    for item in data:
        writer.writerow([str(self._get_field_value(item, h)) for h in headers])
        # NOTE: relies on Flask-Admin implementation detail: ._get_field_value
    response = make_response(buffer.getvalue())
    response.headers['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)
    response.headers['Content-Type'] = 'text/csv; charset=utf-8'
    return response
