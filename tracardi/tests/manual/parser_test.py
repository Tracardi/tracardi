from pprint import pprint

from tracardi.process_engine.tql.parser import Parser
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.utils.dictonary import flatten

if __name__ == "__main__":

    data = {
        "a": {
            "b": 1,
            "c": [1,2,3],
            "d": {"aa": 1},
            "e": "test",
            'f': 1,
            'g': True,
            'h': None,
            'i': "2021-01-10"
        }
    }

    p = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')
    # t = p.parse("a.b=1 and (a.c == 2 or a.c == [1,2,3])")
    # t = p.parse("datetime(a.i) between datetime(\"2020-01-01\") and datetime(\"2022-01-01\")")
    # t = p.parse("a.d.aa between 2 and 1")
    # t = p.parse("a.e == \"test\"")
    # t = p.parse("a.b == a.f")
    # t = p.parse("a.g == TRUE")
    # t = p.parse("a.h == null")
    # t = p.parse("a.b <= 1")
    t = p.parse("a.h.h not exists")
    pprint(t)
    query = ExprTransformer(data=flatten(data)).transform(t)
    pprint(query)
    print(data)