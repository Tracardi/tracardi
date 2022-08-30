import datetime
import logging

import dateparser
import pytimeparse
import pytz

from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.notation.dot_accessor import DotAccessor
from typing import Union

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

    __mapping = {
        ("now", 0): datetime.datetime.now,
        ("utcnow", 0): datetime.datetime.utcnow,
        ("datetime", 1): "_datetime1",
        ("now", 1): "_now1",
        ("now.offset", 1): "_now_offset1",
        ("now.timezone.offset", 2): "_now_timezone_offset2",
        ("datetime.offset", 2): "_datetime_offset2",
        ("datetime.timezone", 2): "_datetime_timezone2",
        ("datetime.from_timestamp", 1): "_datetime_from_timestamp1",
        ("now.timezone", 1): "_now_timezone1",
        ("lowercase", 1): "_lowercase1",
        ("uppercase", 1): "_uppercase1"
    }

    def _datetime1(self, value):
        return self.__parse_datetime(value)

    def _now1(self, timezone):
        return datetime.datetime.now(pytz.timezone(timezone))

    def _now_offset1(self, offset):
        passed_seconds = self.__parse_offset(offset)
        return datetime.datetime.now() + datetime.timedelta(seconds=passed_seconds)

    def _now_timezone_offset2(self, timezone, offset):
        passed_seconds = self.__parse_offset(offset)
        timezone = pytz.timezone(timezone)
        return datetime.datetime.now(timezone) + datetime.timedelta(seconds=passed_seconds)

    def _datetime_offset2(self, date, offset):
        passed_seconds = self.__parse_offset(offset)
        date = self.__parse_datetime(date)
        return date + datetime.timedelta(seconds=passed_seconds)

    def _datetime_timezone2(self, date, timezone):
        date = self.__parse_datetime(date)
        timezone = pytz.timezone(timezone)
        tz_date = date.replace(tzinfo=pytz.utc).astimezone(timezone)
        return timezone.normalize(tz_date)

    def _datetime_from_timestamp1(self, timestamp):
        return datetime.datetime.fromtimestamp(timestamp)

    def _now_timezone1(self, timezone):
        timezone = pytz.timezone(timezone)
        tz_date = datetime.datetime.now().replace(tzinfo=pytz.utc).astimezone(timezone)
        return timezone.normalize(tz_date)

    def _lowercase1(self, value):
        if isinstance(value, str):
            return value.lower()
        return value

    def _uppercase1(self, value):
        if isinstance(value, str):
            return value.upper()
        return value

    def __init__(self, dot, *args, **kwargs):
        if not isinstance(dot, DotAccessor):
            raise ValueError("Data passed to ExprTransformer must be type of DotAccessor.")
        super().__init__(*args, **kwargs)
        self.namespace('uql_function__', FunctionTransformer())
        self._dot = dot

    def expr(self, args):
        result = args[0]

        if isinstance(result, ValueError):
            raise result

        return args[0]

    def and_expr(self, args):
        # return args
        value1, _, value2 = args

        if isinstance(value1, ValueError) or isinstance(value1, MissingValue):
            return value1

        if value1 is False:
            return False

        return value1 and value2

    def or_expr(self, args):
        # return args
        value1, _, value2 = args

        if value1 is True:
            return True

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

        if isinstance(value1, ValueError) or isinstance(value1, MissingValue):
            return value1
        if isinstance(value2, ValueError) or isinstance(value2, MissingValue):
            return value2

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

        # Check if any of the parameters is missing
        for x in values:
            # If so return missing value
            if isinstance(x, MissingValue):
                return x

        method = self.__mapping.get((function, len(values)), None)
        if method is None:
            raise ValueError("Unknown operation `{}`".format(function))

        func = getattr(self, method) if isinstance(method, str) else method
        try:
            return func(*values)
        except Exception as e:
            return ValueError(str(e))

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
        return args[0].label not in self._dot or args[0].value is None or (
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

    def op_contains(self, args):
        container, _, contained = args
        if isinstance(container.value, str) and not isinstance(contained, str):
            raise ValueError("Value tested for containing value is of type string, but value tested for being "
                             "contained is not. {} given.".format(type(contained)))
        if not (isinstance(container.value, str) or isinstance(container.value, list)):
            raise ValueError(
                "Value tested for containing other value, should be array or string. {} given.".format(
                    type(container.value)
                )
            )

        return contained in container.value

    def op_startswith(self, args):
        container, _, prefix = args
        if isinstance(container.value, list):
            if not container.value:
                return False
            return container.value[0] == prefix

        elif isinstance(container.value, str):
            return container.value.startswith(prefix)

        else:
            raise ValueError(
                "Value tested for starting with other value, should be array or string. {} given.".format(
                    type(container.value)
                )
            )

    def op_endswith(self, args):
        container, _, suffix = args
        if isinstance(container.value, list):
            if not container.value:
                return False
            return container.value[-1] == suffix

        elif isinstance(container.value, str):
            return container.value.endswith(suffix)

        else:
            raise ValueError(
                "Value tested for ending with other value, should be array or string. {} given.".format(
                    type(container.value)
                )
            )

    @staticmethod
    def __parse_datetime(value: Union[str, datetime.datetime]) -> datetime.datetime:
        if isinstance(value, datetime.datetime):
            return value
        elif isinstance(value, str):
            value = dateparser.parse(value)
            if not value:
                raise ValueError("Could not parse `{}` as date.. Expected datetime or parsable string.".format(value))
            return value
        raise ValueError("Could not parse `{}` as date. Expected datetime or parsable string.".format(value))

    @staticmethod
    def __parse_offset(value: str) -> Union[int, float]:
        try:
            value = pytimeparse.parse(value)
            if not value:
                raise ValueError("Could not parse value `{}` as time offset.".format(value))
            return value
        except Exception as _:
            raise ValueError("Could not parse value `{}` as time offset.".format(value))
