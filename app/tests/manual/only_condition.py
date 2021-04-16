from unomi_query_language.query.parser import Parser
from unomi_query_language.query.grammar.grammars import read
from pprint import pprint

from unomi_query_language.query.transformers.condition_transformer import ConditionTransformer

p = Parser(read('uql_expr.lark'), start='expr')
t = p.parse(
    """
    properties.name="asasas" and funct() and a=1
    """
)

print(t)
pprint(ConditionTransformer().transform(t))
