from ..statement_templates.sort_stmt_templates import sort_stmt
from ..transformers.sort_transformer import SortTransformer
from ..statement_templates.query_stmt_templates import create_condition_stmt, select_stmt
from ..mappers.uri_mapper import uri_mapper
from ..transformers.condition_transformer import ConditionTransformer
from ..transformers.transformer_namespace import TransformerNamespace


class SelectTransformer(TransformerNamespace):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace('uql_expr__', ConditionTransformer())
        self.namespace('uql_sort__', SortTransformer())

    def expr(self, args):
        return args

    def sort(self, args):
        return 'sort', args

    def select(self, args):
        elements = {k: v for k, v in args}

        query_data_type = elements['DATA_TYPE'] if 'DATA_TYPE' in elements else None

        key = ('select', query_data_type)
        if key in uri_mapper:
            uri, method, status = uri_mapper[key]
        else:
            raise ValueError("Unknown {} {} syntax.".format(key[0], key[1]))

        where = elements['WHERE'] if 'WHERE' in elements else None
        condition = create_condition_stmt(where, query_data_type)

        sort = elements['sort'] if 'sort' in elements else None
        sort = sort_stmt(sort, query_data_type)

        query = select_stmt(elements, condition, sort)

        return query_data_type, uri, method, query, status

    def where(self, args):
        return 'WHERE', args[0]

    def data_type(self, args):
        return 'DATA_TYPE', args[0].value.lower()

    def FRESH(self, args):
        return 'FRESH', args.value.lower()

    def limit(self, args):
        return 'LIMIT', int(args[0].value)

    def offset(self, args):
        return 'OFFSET', int(args[0].value)
