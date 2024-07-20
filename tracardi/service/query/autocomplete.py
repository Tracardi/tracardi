from dataclasses import dataclass
from typing import List, Optional, Tuple, Dict, Any, Callable

from lark import Lark, Token
from lark.lexer import TerminalDef

from tracardi.service.storage.elastic.interface import raw as raw_db

from .tql_schema import schema

# ([^\s\"]+|(?<!\\)([\"].*?(?<!\\)[\"]))
# %import common.ESCAPED_STRING

APPEND_NONE = None
APPEND_BOTH = 0
APPEND_BEFORE = -1
APPEND_AFTER = 1


@dataclass
class Value:
    token: str
    value: Optional[str] = None


@dataclass
class AutocompleteValue:
    next_token: Value
    current_token: Value


@dataclass
class TokenSettings:
    func: Callable
    name: str
    token: str
    description: Optional[Callable] = None
    space: Optional[int] = None
    color: Optional[str] = "#ef6c00"


class HashableDict(Dict):
    def key(self):
        return self['value']


class Values:

    @staticmethod
    def _filter(current_value, fields):
        return [field for field in fields if current_value in field and current_value != field]

    @staticmethod
    async def _quote_description(value):
        return "Quote"

    @staticmethod
    async def _quote(last: dict[str, Any], current: Value):
        if current.token == "QUOTE":
            return []
        return ['"']

    @staticmethod
    async def _op_description(value):
        descriptions = {
            "=": "Equals",
            "!=": "Not Equals",
            ">=": "Greater or equal than",
            "<=": "Lower or equal than",
            "<": "Lower than",
            ">": "Greater than",
        }
        return descriptions[value]

    @staticmethod
    async def _op(last: dict[str, Any], current: Value):
        current_value = current.value
        operations = ['=', '!=', '>=', '<=', '<', '>']
        if current.token == "OP":
            return Values._filter(current_value, operations)
        return operations

    @staticmethod
    async def _field_description(value):
        return ""

    async def _field(self, last: dict[str, Any], current: Value):
        current_value = current.value
        fields = await raw_db.get_mapping_fields(self.index)
        if current_value.strip() == "":
            return fields
        if current.token == "FIELD":
            filtered = self._filter(current_value, fields)
            return sorted(filtered)
        return fields

    @staticmethod
    async def _boolean_description(value):
        return f"Boolean `{value}`"

    @staticmethod
    async def _and_link(last: dict[str, Any], current: Value):
        if current.token == "AND":
            return []
        return ['AND']

    @staticmethod
    async def _or_link(last: dict[str, Any], current: Value):
        if current.token == "OR":
            return []
        return ['OR']

    @staticmethod
    async def _bracket_description(value):
        return "Closing bracket" if value == ")" else "Opening bracket"

    @staticmethod
    async def _open_bracket(last: dict[str, Any], current: Value):
        if current.token == "(":
            return []
        return ['(']

    @staticmethod
    async def _close_bracket(last: dict[str, Any], current: Value):
        if current.token == "(":
            return []
        return [')']

    @staticmethod
    async def _value_description(value):
        return ""

    async def _value(self, last: dict[str, Any], current: Value):
        field = last['FIELD']
        result = await raw_db.get_unique_field_values(self.index, field)
        values = [item.get("key_as_string", item.get("key", None)) for item in result.aggregations("fields").buckets()]
        if current.token == "VALUE":
            return self._filter(current.value, values)
        return values

    def __init__(self, index):
        self.index = index
        self.tokens: Dict[str, TokenSettings] = {
            "QUOTE": TokenSettings(func=self._quote, token="QUOTE", name="quote", description=self._quote_description,
                                   space=APPEND_NONE, color="#546e7a"),
            "OP": TokenSettings(func=self._op, token="OP", name="operation", description=self._op_description,
                                space=APPEND_AFTER),
            "FIELD": TokenSettings(func=self._field, token="FIELD", name="field", description=self._field_description,
                                   space=APPEND_NONE, color="#00acc1"),
            "AND": TokenSettings(func=self._and_link, token="AND", name="and", description=self._boolean_description,
                                 space=APPEND_BOTH, color="#689f38"),
            "OR": TokenSettings(func=self._or_link, token="OR", name="or", description=self._boolean_description,
                                space=APPEND_BOTH, color="#689f38"),
            "OPEN_BRACKET": TokenSettings(func=self._open_bracket, token="BRACKET", name="bracket",
                                          description=self._bracket_description,
                                          space=APPEND_NONE, color="#e64a19"),
            "CLOSE_BRACKET": TokenSettings(func=self._close_bracket, token="BRACKET", name="bracket",
                                           description=self._bracket_description,
                                           space=APPEND_NONE, color="#e64a19"),
            "VALUE": TokenSettings(func=self._value, name="value", token="VALUE", description=self._value_description,
                                   space=APPEND_NONE, color="#afb42b")
        }

    async def get(self, autocomplete_item: AutocompleteValue, last):
        next_values = []
        current_values = []
        next_token = autocomplete_item.next_token.token
        current_token = autocomplete_item.current_token.token
        if next_token in self.tokens:
            next_token = self.tokens[next_token]
            for value in await next_token.func(last=last, current=autocomplete_item.current_token):
                next_values.append(HashableDict({
                    "value": value,
                    "token": next_token.token,
                    "name": next_token.name,
                    "desc": await next_token.description(value) if next_token and next_token.description is not None else "",
                    "space": next_token.space,
                    "color": next_token.color
                }))
            current_token = self.tokens[current_token]
            for value in await current_token.func(last=last, current=autocomplete_item.current_token):
                current_values.append(HashableDict({
                    "value": value,
                    "token": current_token.token,
                    "name": current_token.name,
                    "desc": await current_token.description(value) if next_token and next_token.description is not None else "",
                    "space": current_token.space,
                    "color": current_token.color
                }))

        return next_values, current_values


parser = Lark(schema, parser="lalr")


class KQLAutocomplete:
    def __init__(self, index):
        self.last = {}
        self.current = None
        self.values = Values(index)

    def _get_terms(self, query):
        interactive = parser.parse_interactive(query)
        for token in interactive.iter_parse():  # type: Token
            self.current = token
            self.last[token.type] = token

        interactive.exhaust_lexer()

        return interactive.accepts()

    def autocomplete_token(self, query: str) -> List[AutocompleteValue]:
        next_terms = self._get_terms(query)
        for next_term in next_terms:
            for term_def in parser.terminals:  # type: TerminalDef

                if term_def.name == next_term:
                    yield AutocompleteValue(
                        next_token=Value(token=term_def.name),
                        current_token=Value(
                            token=self.current.type if self.current else term_def.name,
                            value=self.current.value if self.current else query)
                    )

    @staticmethod
    def _get_unique(values):
        if not values:
            return []

        result = {}
        for value in values:
            if value.key() not in result:
                result[value.key()] = dict(value)
        return list(result.values())

    async def autocomplete(self, query: str) -> Tuple[list, Value]:
        next_values = []
        current_values = []
        for autocomplete_item in self.autocomplete_token(query):
            _next_values, _current_values = await self.values.get(autocomplete_item, self.last)
            next_values += _next_values
            current_values += _current_values
        return self._get_unique(current_values + next_values), \
               Value(token=self.current.type, value=self.current.value) if self.current else None
