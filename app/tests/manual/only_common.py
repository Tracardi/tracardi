from unomi_query_language.query.parser import Parser
from unomi_query_language.query.grammar.grammars import read
from pprint import pprint

from unomi_query_language.query.transformers.common_transformer import CommonTransformer
from unomi_query_language.query.transformers.function_transformer import FunctionTransformer

p = Parser(read('uql_common.lark'), start='ESCAPED_STRING')
t = p.parse(
    """
    "asasasa"
    """
)

print(t)
pprint(CommonTransformer().transform(t))
