import datetime
import logging

import dateparser
import pytimeparse
import pytz

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.notation.dot_accessor import DotAccessor

from ..domain.field import Field
from .function_transformer import FunctionTransformer
from .transformer_namespace import TransformerNamespace
from ..domain.missing_value import MissingValue

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


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
    'exists': 'exists',
    'not exists': 'not exists',
    'startsWith': 'starts with',  # todo: implement,
    'endsWith': 'ends with',  # todo: implement,
    'matchesRegex': 'regex',  # todo: implement,
    'in': 'in',  # todo: implement,
    'not in': 'not in',  # todo: implement,
    'isDay': 'is day',  # todo: implement,
    'isNotDay': 'is not day',  # todo: implement,
}


class ExprTransformer(TransformerNamespace):

    def __init__(self, dot, *args, **kwargs):
        if not isinstance(dot, DotAccessor):
            raise ValueError("Data passed to ExprTransformer must be type of DotAccessor.")
        super().__init__(*args, **kwargs)
        self.namespace('uql_function__', FunctionTransformer())
        self._dot = dot

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
        return Field(args.value, self._dot)

    def OP(self, args):
        return args.value

    def OP_NUMBER(self, args):
        return float(args.value)

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
        elif operation == '=<':
            return value1 <= value2
        elif operation == '=>':
            return value1 >= value2

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

    def op_value_or_field(self, args):
        if len(args) != 1:
            raise ValueError("Expected 1 arg.")

        value = args[0]
        if isinstance(value, Field):
            return value.value

        return value

    def op_compound_value(self, args):

        function = args[0]

        if len(args) > 1:
            values = args[1:]
        else:
            values = []

        if not values or values[0] is None:
            if function == 'now':
                return datetime.datetime.now()
            if function == 'utcnow':
                return datetime.datetime.utcnow()
        else:
            if function == 'datetime' and len(values) == 1:
                value = values[0]

                if isinstance(value, str):
                    date = dateparser.parse(value)

                    if not date:
                        raise ValueError("Could not parse date `{}`".format(value))
                elif isinstance(value, datetime.datetime):
                    return value
                else:
                    raise ValueError(
                        "Value of `{}` must be string to compare it with datetime. Type of {} given".format(value,
                                                                                                            type(
                                                                                                                value)))
                return date

            if function == 'now' and len(values) == 1:
                timezone = values[0]
                return datetime.datetime.now(pytz.timezone(timezone))

            if function == 'now.offset' and len(values) == 1:
                offset = values[0]
                passed_seconds = pytimeparse.parse(offset)
                if passed_seconds is None:
                    raise ValueError("Could not parse `{}`".format(offset))
                return datetime.datetime.now() + datetime.timedelta(seconds=passed_seconds)

            if function == 'now.timezone.offset' and len(values) == 2:
                timezone, offset = values
                passed_seconds = pytimeparse.parse(offset)
                if passed_seconds is None:
                    raise ValueError("Could not parse `{}`".format(offset))
                timezone = pytz.timezone(timezone)
                return datetime.datetime.now(timezone) + datetime.timedelta(seconds=passed_seconds)

            if function == 'datetime.offset' and len(values) == 2:
                date, offset = values

                if isinstance(date, MissingValue):
                    return MissingValue

                passed_seconds = pytimeparse.parse(offset)
                if passed_seconds is None:
                    raise ValueError("Could not parse `{}`".format(offset))

                if isinstance(date, str):
                    date = dateparser.parse(date)

                return date + datetime.timedelta(seconds=passed_seconds)

            if function == 'datetime.timezone' and len(values) == 2:
                date, timezone = values

                if isinstance(date, str):
                    date = dateparser.parse(date)

                timezone = pytz.timezone(timezone)
                tz_date = date.replace(tzinfo=pytz.utc).astimezone(timezone)
                return timezone.normalize(tz_date)

            if function == 'datetime.from_timestamp' and len(values) == 1:
                timestamp, = values
                return datetime.datetime.fromtimestamp(timestamp)

            if function == 'now.timezone' and len(values) == 1:
                timezone, = values
                timezone = pytz.timezone(timezone)
                tz_date = datetime.datetime.now().replace(tzinfo=pytz.utc).astimezone(timezone)
                return timezone.normalize(tz_date)

            if function == 'lowercase' and len(values) == 1:
                value = values[0]
                if isinstance(value, str):
                    return value.lower()
                return value

            if function == 'uppercase' and len(values) == 1:
                value = values[0]
                if isinstance(value, str):
                    return value.upper()
                return value

        raise ValueError("Unknown type `{}`".format(function))

    def op_field_sig(self, args):
        return args[0]

    def op_value_sig(self, args):
        return args[0]

    def op_is_null(self, args):
        return args[0].value is None

    def op_is_not_null(self, args):
        return args[0].value is not None

    def op_exists(self, args):
        return args[0].label in self._dot

    def op_not_exists(self, args):
        return args[0].label not in self._dot

    def op_empty(self, args):
        return args[0].label not in self._dot or args[0].value is None \
               or (
                       (
                               isinstance(args[0].value, str)
                               or isinstance(args[0].value, list)
                               or isinstance(args[0].value, dict)
                       ) and len(args[0].value) == 0
               )

    def op_not_empty(self, args):
        try:
            return not self.op_empty(args)
        except AttributeError:
            return True
