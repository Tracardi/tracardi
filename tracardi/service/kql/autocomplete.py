from dataclasses import dataclass
from hashlib import sha1
from typing import List, Optional, Generator, Tuple, Dict

from lark import Lark, Token
from lark.lexer import TerminalDef

from tracardi.service.storage.driver import storage

schema = r"""
?start: multi_expr
multi_expr: statement 
            | (and_expr|or_expr) ((OR|AND) (and_expr|or_expr))*
or_expr: or_multiple_joins
            | or_join
and_expr: and_multiple_joins
            | and_join
or_multiple_joins: (OPEN_BRACKET ( or_join (OR statement)*) CLOSE_BRACKET)
and_multiple_joins: (OPEN_BRACKET ( and_join (AND statement)*) CLOSE_BRACKET)

or_join:    (statement|or_multiple_joins|and_multiple_joins) OR (statement|or_multiple_joins|and_multiple_joins)
and_join:   (statement|or_multiple_joins|and_multiple_joins) AND (statement|or_multiple_joins|and_multiple_joins)
statement: FIELD OP (QUOTE VALUE QUOTE | VALUE)
OPEN_BRACKET: "("
CLOSE_BRACKET: ")"
QUOTE:      /[\"]/
VALUE:      /([^\s\"]+|(?<!\\)([\"].*?(?<!\\)[\"]))/ 
            | "*"
FIELD:      /[a-zA-z_\.-0-9]+/
SPACE:      /[\s]+/
operator:   ":" 
            | ">=" 
            | "<=" 
            | "<" 
            | ">"
OP: /(:|<=|>=|>|<)/
AND: /AND/i
OR: /OR/i

%ignore /\s+/
"""


# (\w+|(?<!\\)([\"].*?(?<!\\)[\"]))
# %import common.ESCAPED_STRING

@dataclass
class Value:
    token: str
    value: Optional[str] = None


@dataclass
class AutocompleteValue:
    next_token: Value
    current_token: Value


class HashableDict(Dict):
    def __hash__(self):
        return sha1(self['value'].encode())


class Values:

    @staticmethod
    async def _quote(field, current_value):
        return ['"']

    @staticmethod
    async def _op(field, current_value):
        return [':', '>=', '<=', '<', '>']

    async def _field(self, field, current_value):
        fields = await storage.driver.raw.get_mapping_fields(self.index)
        if current_value.strip() == "":
            return fields
        filtered = [field for field in fields if field.startswith(current_value)]
        return sorted(filtered)

    @staticmethod
    async def _and_link(field, current_value):
        return ['AND']

    @staticmethod
    async def _or_link(field, current_value):
        return ['OR']

    @staticmethod
    async def _open_bracket(field, current_value):
        return ['(']

    @staticmethod
    async def _close_bracket(field, current_value):
        return [')']

    async def _value(self, field, current_value):
        print(self.index, field)
        result = await storage.driver.raw.get_unique_field_values(self.index, field)
        return [item.get("key_as_string", item.get("key", None)) for item in result.aggregations("fields").buckets()]

    def __init__(self, index):
        self.index = index
        self.values = {
            "QUOTE": self._quote,
            "OP": self._op,
            "FIELD": self._field,
            "AND": self._and_link,
            "OR": self._or_link,
            "OPEN_BRACKET": self._open_bracket,
            "CLOSE_BRACKET": self._close_bracket,
            "VALUE": self._value
        }
        self.names = {
            "QUOTE": ("quote", "String quote"),
            "OP": ("operation", "JOIN operation"),
            "FIELD": ("field", "Index field"),
            "AND": ("and", "Boolean AND operation"),
            "OR": ("or", "Boolean OR operation"),
            "OPEN_BRACKET": ("bracket", "OPEN bracket"),
            "CLOSE_BRACKET": ("bracket", "CLOSE bracket"),
            "VALUE": ("value", "FIELD value")
        }

    async def get(self, autocomplete_item: AutocompleteValue, last_field):
        next_values = []
        current_values = []
        next_token = autocomplete_item.next_token.token
        current_token = autocomplete_item.current_token.token
        if next_token in self.values:
            for value in await self.values[next_token](
                    field=last_field,
                    current_value=autocomplete_item.current_token.value):
                next_values.append(HashableDict({
                    "value": value,
                    "token": self.names[next_token][0],
                    "desc": self.names[next_token][1],
                }))
            for value in await self.values[current_token](
                    field=last_field,
                    current_value=autocomplete_item.current_token.value):
                current_values.append(HashableDict({
                    "value": value,
                    "token": self.names[current_token][0],
                    "desc": self.names[current_token][1],
                }))

        return next_values, current_values


parser = Lark(schema, parser="lalr")


class KQLAutocomplete:
    def __init__(self, index):
        self.last_field = None
        self.last_value = None
        self.last_op = None
        self.current = None
        self.values = Values(index)

    def _get_terms(self, query):
        interactive = parser.parse_interactive(query)
        for token in interactive.iter_parse():  # type: Token
            self.current = token
            self.last_token = token.type
            if token.type == "FIELD":
                self.last_field = token.value
            elif token.type == "OP":
                self.last_op = token.value
            elif token.type == "VALUE":
                self.last_value = token.value

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

    async def autocomplete(self, query: str):
        next_values = []
        current_values = []
        for autocomplete_item in self.autocomplete_token(query):
            _next_values, _current_values = await self.values.get(autocomplete_item, self.last_field)
            next_values += _next_values
            current_values += _current_values
        if query.strip() == "":
            return next_values
        return current_values + next_values


if __name__ == "__main__":
    import asyncio


    async def main():
        ac = KQLAutocomplete(index="event")
        print(await ac.autocomplete(""))


    asyncio.run(main())
