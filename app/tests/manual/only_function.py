from unomi_query_language.query.parser import Parser
from unomi_query_language.query.grammar.grammars import read
from pprint import pprint
from unomi_query_language.query.transformers.function_transformer import FunctionTransformer

p = Parser(read('uql_function.lark'), start='function')
t = p.parse(
    """
    funct(1,2)
    """
)

print(t)
pprint(FunctionTransformer().transform(t))
