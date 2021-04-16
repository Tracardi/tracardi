from ..statement_templates.query_stmt_templates import create_rule_stmt, create_condition_stmt
from ..statement_templates.actions_stmt_templates import create_actions_group_stmt
from ..mappers.uri_mapper import uri_mapper
from .common_transformer import CommonTransformer
from .condition_transformer import ConditionTransformer
from .function_transformer import FunctionTransformer
from .meta_transformer import MetaTransformer


class CreateRuleTransformer(MetaTransformer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace('uql_expr__', ConditionTransformer())
        self.namespace('uql_function__', FunctionTransformer())
        self.namespace('uql_common__', CommonTransformer())
        self.namespace('uql_meta__', MetaTransformer())

    def create_rule(self, args):

        elements = {k: v for k, v in args}

        query_data_type = elements['DATA_TYPE'] if 'DATA_TYPE' in elements else None
        key = ('create', query_data_type)
        if key not in uri_mapper:
            raise ValueError("Unknown {} {} syntax.".format(key[0], key[1]))

        uri, method, status = uri_mapper[key]

        when = elements['WHEN'] if 'WHEN' in elements else None
        condition = create_condition_stmt(when, query_data_type)

        then = elements['THEN'] if 'THEN' in elements else None
        actions = create_actions_group_stmt(then)
        query = create_rule_stmt(elements, condition, actions)

        return query_data_type, uri, method, query, status

    def when(self, args):
        return 'WHEN', args[1]

    def then(self, args):
        return 'THEN', args[1]

    def data_type(self, args):
        return 'DATA_TYPE', args[0].value.lower()

    def functions(self, args):
        return 'FUNCTIONS', args

    def function(self, args):
        return args

    def expr(self, args):
        return args


