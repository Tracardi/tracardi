from typing import List

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
operator:   ":" 
            | ">=" 
            | "<=" 
            | "<" 
            | ">"
OP: /(:|<=|>=|>|<)/
AND: /AND/i
OR: /OR/i

%import common.ESCAPED_STRING
%ignore /\s+/
"""
# (\w+|(?<!\\)([\"].*?(?<!\\)[\"]))

class Values:

    @staticmethod
    async def _quote(field):
        return ['"']

    @staticmethod
    async def _op(field):
        return [':', '>=', '<=', '<', '>']

    async def _field(self, field):
        fields = await storage.driver.raw.get_mapping_fields(self.index)
        return fields

    @staticmethod
    async def _and_link(field):
        return ['AND']

    @staticmethod
    async def _or_link(field):
        return ['OR']

    @staticmethod
    async def _open_bracket(field):
        return ['(']

    @staticmethod
    async def _close_bracket(field):
        return [')']

    async def _value(self, field):
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

    async def get(self, token, field) -> List[dict]:
        values = []
        if token in self.values:
            for value in await self.values[token](field):
                values.append({
                    "value": value,
                    "token": self.names[token][0],
                    "desc": self.names[token][1],
                })
        return values


parser = Lark(schema, parser="lalr")


class KQLAutocomplete:
    def __init__(self, index):
        self.last_field = None
        self.last_value = None
        self.last_op = None
        self.values = Values(index)

    def _get_terms(self, query):
        interactive = parser.parse_interactive(query)
        for token in interactive.iter_parse():  # type: Token
            if token.type == "FIELD":
                self.last_field = token.value
            elif token.type == "OP":
                self.last_op = token.value
            elif token.type == "VALUE":
                self.last_value = token.value
        interactive.exhaust_lexer()

        return interactive.accepts()

    def autocomplete_token(self, query: str):
        terms = self._get_terms(query)
        for term in terms:

            for term_def in parser.terminals:  # type: TerminalDef

                if term_def.name == term:
                    yield term_def.name

    async def autocomplete(self, query: str):
        values = []
        for token in self.autocomplete_token(query):
            values += await self.values.get(token, self.last_field)

        return values


if __name__ == "__main__":
    import asyncio


    async def main():
        ac = KQLAutocomplete(index="event")
        print(await ac.autocomplete("metadata.time.insert:"))


    asyncio.run(main())
