from query.transformers.sort_transformer import SortTransformer
from unomi_query_language.query.parser import Parser
from unomi_query_language.query.grammar.grammars import read

from unomi_query_language.query.transformers.select_transformer import SelectTransformer

p = Parser(read('uql_sort.lark'), start='sort')
t = p.parse(
    """
    # SELECT EVENT WHERE event:type="view"
    SORT BY version ASC, ala.x DESC
    """
)
#
query = SortTransformer().transform(t)
print(query)
