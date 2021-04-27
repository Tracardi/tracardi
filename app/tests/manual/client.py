import json

import lark

from unomi_query_language.query.dispatcher import Dispatcher, Host
from unomi_query_language.query.parser import Parser
from pprint import pprint

from unomi_query_language.query.rules.grammars import select
from unomi_query_language.query.transformers.select_transformer import SelectTransformer

host = Host('localhost', port=8181, protocol='http').credentials('karaf','karaf')
dispatcher = Dispatcher(host)
print("connected to {}".format(host))

while True:
    uql = input('uql>')
    try:
        p = Parser(select(), start="select")
        tree = p.parse(uql)

        query = SelectTransformer().transform(tree)
        uri, method, body = query
        print(f"Fetching {uql} from {method} {host}{uri}")
        response, request = dispatcher.fetch(query)
        if response.status_code == 200:
            pprint(json.loads(response.content))
        else:
            print(response.content)
    except lark.exceptions.UnexpectedCharacters as e:
        print(str(e))
