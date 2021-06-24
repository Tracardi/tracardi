import dateparser

from ..domain.field import Field
from .function_transformer import FunctionTransformer
from .transformer_namespace import TransformerNamespace

operation_mapper = {
    "between": "between",
    "=": "equals",
    "!=": "notEquals",
    "<>": "notEquals",  # todo implement in parser
    '>=': 'greaterThanOrEqualTo',
    '<=': 'lessThanOrEqualTo',
    '>': 'greaterThan',
    '<': 'lessThan',
    'is null': 'isNull',
    'startsWith': 'starts with',  # todo: implement,
    'endsWith': 'ends with',  # todo: implement,
    'matchesRegex': 'regex',  # todo: implement,
    'in': 'in',  # todo: implement,
    'not in': 'not in',  # todo: implement,
    'isDay': 'is day',  # todo: implement,
    'isNotDay': 'is not day',  # todo: implement,
}


class ExprTransformer(TransformerNamespace):

    def __init__(self, data, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace('uql_function__', FunctionTransformer())
        self._data = data

    def expr(self, args):
        return args[0]

    def and_expr(self, args):
        # return args
        value1, _, value2 = args
        return value1 and value2

    def or_expr(self, args):
        # return args
        value1, _, value2 = args
        return value1 or value2

    def OP_FIELD(self, args):
        if args.value not in self._data:
            raise ValueError("Field `{}` does not exist".format(args.value))
        value = self._data[args.value]
        return Field(args.value, value)

    def OP(self, args):
        return args.value

    def OP_INTEGER(self, args):
        return int(args.value)

    def OP_STRING(self, args):
        return args.value.strip('"')

    @staticmethod
    def _compare(operation, value1, value2):
        if operation == '==':
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
        return args

    def op_range(self, args):
        return args

    def op_between(self, args):
        field, _, values = args
        value1, value2 = values
        return value1 <= field <= value2

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

    def op_compound_field(self, args):
        value_type, field = args
        value = field.value
        if value_type == 'datetime':

            if not isinstance(value, str):
                raise ValueError(
                    "Value of `{}` must be string to compare it with datetime. Type of {} given".format(field.label,
                                                                                                        type(value)))

            date = dateparser.parse(value)
            if not date:
                raise ValueError("Could not parse date `{}`".format(value))
            return date

        raise ValueError("Unknown type `{}`".format(value_type))

    def op_field_sig(self, args):
        return args[0]

    def op_value_sig(self, args):
        return args[0]

    def op_is_null(self, args):
        return args[0].value is None

    def op_exists(self, args):
        return args[0].label in self._data

    def op_not_exists(self, args):
        return args[0].label not in self._data