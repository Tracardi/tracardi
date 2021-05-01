import json

from unomi_query_language.query.dispatcher import Host, Dispatcher
from unomi_query_language.query.parser import Parser
from unomi_query_language.query.grammar.grammars import read
from pprint import pprint

from unomi_query_language.query.transformers.select_transformer import SelectTransformer

p = Parser(read('uql_select.lark'), start='select')
t = p.parse(
    """
    SELECT PROFILE
    """
)

query = SelectTransformer().transform(t)

host = Host('localhost', port=8181, protocol='http').credentials('karaf','karaf')
dispatcher = Dispatcher(host)
response, _ = dispatcher.fetch(query)
if response.status_code == 200:
    pprint(json.loads(response.content))
else:
    print(response.content)
