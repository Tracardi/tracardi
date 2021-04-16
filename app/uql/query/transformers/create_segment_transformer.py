from ..statement_templates.query_stmt_templates import create_segment_stmt, create_condition_stmt
from ..mappers.uri_mapper import uri_mapper
from .condition_transformer import ConditionTransformer
from .meta_transformer import MetaTransformer


class CreateSegmentTransformer(MetaTransformer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace('uql_expr__', ConditionTransformer())

    def create_segment(self, args):
        elements = {k: v for k, v in args}

        query_data_type = elements['DATA_TYPE'] if 'DATA_TYPE' in elements else None
        key = ('create', query_data_type)
        if key not in uri_mapper:
            raise ValueError("Unknown {} {} syntax.".format(key[0], key[1]))

        uri, method, status = uri_mapper[key]

        when_condition = elements['WHEN'] if 'WHEN' in elements else None
        condition = create_condition_stmt(when_condition, query_data_type)
        query = create_segment_stmt(elements, condition)

        return query_data_type, uri, method, query, status

    def when(self, args):
        return 'WHEN', args[0]

    def then(self, args):
        return 'THEN', args[0]

    def data_type(self, args):
        return 'DATA_TYPE', args[0].value.lower()


