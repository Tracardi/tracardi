import dateparser
from ..domain.elastic_condition import ElasticFieldCondition
from .function_transformer import FunctionTransformer
from .transformer_namespace import TransformerNamespace
from ..domain.operations import OrOperation
from ..utils.value_compressions import Values


# operation_mapper = {
#     "between": "between",
#     "=": "equals",
#     "!=": "notEquals",
#     "<>": "notEquals",  # todo implement in parser
#     '>=': 'greaterThanOrEqualTo',
#     '<=': 'lessThanOrEqualTo',
#     '>': 'greaterThan',
#     '<': 'lessThan',
#     'is null': 'isNull',
#     'startsWith': 'starts with',  # todo: implement,
#     'endsWith': 'ends with',  # todo: implement,
#     'matchesRegex': 'regex',  # todo: implement,
#     'in': 'in',  # todo: implement,
#     'not in': 'not in',  # todo: implement,
#     'isDay': 'is day',  # todo: implement,
#     'isNotDay': 'is not day',  # todo: implement,
# }


class FilterTransformer(TransformerNamespace):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace('uql_function__', FunctionTransformer())

    def expr(self, args):
        return args[0]

    def and_expr(self, args):
        values = Values()

        # return args
        value1, _, value2 = args

        values.append_or_value(value1)
        values.append_or_value(value2)

        return OrOperation({
            "bool": {
                "must": values.values
            }
        })

    def or_expr(self, args):
        values = Values()

        # return args
        value1, _, value2 = args

        values.append_and_value(value1)
        values.append_and_value(value2)

        return OrOperation({
            "bool": {
                "should": values.values
            }
        })

    def OP_FIELD(self, args):
        return ElasticFieldCondition(args.value)

    def OP(self, args):
        return args.value

    def OP_INTEGER(self, args):
        return int(args.value)

    def OP_STRING(self, args):
        return args.value.strip('"')

    @staticmethod
    def _compare(operation, value1, value2):
        if operation == '=':
            if isinstance(value1, list) and not isinstance(value2, list):
                return value2 in value1
            return value1 == value2
        elif operation == '!=':
            return value1 != value2
        elif operation == '>':
            return value1 > value2
        elif operation == '>=':
            return value1 >= value2
        elif operation == '<':
            return value1 < value2
        elif operation == '<=':
            return value1 <= value2

    def op_condition(self, args):
        value1, operation, value2 = args
        return self._compare(operation, value1, value2)

    def op_array(self, args):
        return args

    def OP_BOOL(self, args):
        return args.lower() == 'true'

    def OP_NULL(self, args):
        return None

    def OP_FLOAT(self, args):
        return float(args.value)

    def op_range(self, args):
        return args

    def op_between(self, args):
        elsatic_field, _, values = args  # type: ElasticFieldCondition, str, list
        value1, value2 = values
        return {
            "range": {
                elsatic_field.field: {
                    "gte": value1,
                    "lte": value2
                }
            }
        }
        # return value1 <= field <= value2

    def op_field_eq_field(self, args):
        value1, operation, value2 = args
        return self._compare(operation, value1, value2)

    def OP_VALUE_TYPE(self, args):
        return args.value

    def op_compound_value(self, args):
        value_type, value = args
        if value_type == 'datetime':

            if not isinstance(value, str):
                raise ValueError(
                    "Value of `{}` must be string to compare it with datetime. Type of {} given".format(value,
                                                                                                        type(value)))

            date = dateparser.parse(value)

            if not date:
                raise ValueError("Could not parse date `{}`".format(value))
            return date
        raise ValueError("Unknown type `{}`".format(value_type))

    @staticmethod
    def op_compound_field(args):
        value_type, field = args  # type: str, ElasticFieldCondition
        raise ValueError("Functions on fields are not permitted. Unknown function `{}`".format(value_type))

    def op_field_sig(self, args):
        return args[0]  # type: ElasticFieldCondition

    def op_value_sig(self, args):
        return args[0]

    def op_is_null(self, args):
        field = args[0]  # type: ElasticFieldCondition
        return {
            "term": {
                field.field: "NULL"
            }
        }

    def op_exists(self, args):
        field = args[0]  # type: ElasticFieldCondition

        return {
            "exists": {
                "field": field.field
            }
        }

    def op_not_exists(self, args):
        field = args[0]  # type: ElasticFieldCondition
        return {
            "bool": {
                "must_not": {
                    "exists": {
                        "field": field.field
                    }
                }
            }
        }
