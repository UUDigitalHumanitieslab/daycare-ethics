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
        data = self.model.query.filter(self.model.id.in_(ids)).all()
        buffer = StringIO.StringIO(b'')
        writer = csv.writer(buffer, delimiter=';')
        writer.writerow(headers)
        for item in data:
            writer.writerow([str(self._get_field_value(item, h)) for h in headers])
        response = make_response(buffer.getvalue())
        response.headers['Content-Disposition'] = 'attachment; filename="votes.csv"'
        response.headers['Content-Type'] = 'text/csv; charset=utf-8'
        return response

    def __init__(self, session, name='Votes', **kwargs):
        super(VotesView, self).__init__(Vote, session, name, **kwargs)
        self.init_actions()
