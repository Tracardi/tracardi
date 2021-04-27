import json

from unomi_query_language.query.dispatcher import Host, Dispatcher
from unomi_query_language.query.parser import Parser
from unomi_query_language.query.grammar.grammars import read
from pprint import pprint
from unomi_query_language.query.transformers.delete_transformer import DeleteTransformer
p = Parser(read('uql_delete.lark'), start='delete')
t = p.parse(
    "delete rule \"number-of-views\""
)

query = DeleteTransformer().transform(t)
print(query)
host = Host('localhost', port=8181, protocol='http').credentials('karaf','karaf')
dispatcher = Dispatcher(host)
response, exp_status = dispatcher.fetch(query)
if response.status_code == exp_status:
    pprint(json.loads(response.content))
else:
    print(response.content)