from ...process_engine.tql.parser import Parser
from ...process_engine.tql.transformer.expr_transformer import ExprTransformer
from ...process_engine.tql.utils.dictonary import flatten

data = {
    "a": {
        "b": 1,
        "c": [1, 2, 3],
        "d": {"aa": 1},
        "e": "test",
        'f': 1,
        'g': True,
        'h': None,
        'i': "2021-01-10"
    }
}
data = flatten(data)

parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')


def test_tql_operations():
    tree = parser.parse("a.d.aa between 1 and 2")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.e == \"test\"")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b == a.f")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.g == True")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.h == null")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b == 1")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b >= 1")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b <= 1")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b > 0")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b < 2")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) == datetime(\"2021-01-10\")")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) <= datetime(\"2021-01-10\")")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) >= datetime(\"2021-01-10\")")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) < datetime(\"2021-01-11\")")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) > datetime(\"2021-01-09\")")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) < datetime(\"2021-01-10 00:00:01\")")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.h is null")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) between datetime(\"2020-01-01\") and datetime(\"2022-01-01\")")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.h exists")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.h.h not exists")
    assert ExprTransformer(data=data).transform(tree)


def test_tql_false_operations():
    tree = parser.parse("a.d.aa between 3 and 4")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.e != \"test\"")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b != a.f")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.g != True")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.h != null")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b != 1")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b > 1")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b < 1")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b > 0")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.b > 2")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) != datetime(\"2021-01-10\")")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) < datetime(\"2021-01-10\")")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) > datetime(\"2021-01-10\")")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) > datetime(\"2021-01-11\")")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) < datetime(\"2021-01-09\")")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) > datetime(\"2021-01-10 00:00:01\")")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.h != null")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("datetime(a.i) between datetime(\"2022-01-01\") and datetime(\"2023-01-01\")")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.h not exists")
    assert not ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.h.h exists")
    assert not ExprTransformer(data=data).transform(tree)


def test_tql_bool_operations():
    tree = parser.parse("a.d.aa between 1 and 2 and a.e == \"test\"")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.d.aa between 1 and 2 or a.e != \"test\"")
    assert ExprTransformer(data=data).transform(tree)

    tree = parser.parse("a.d.aa between 2 and 3 and a.e != \"test\"")
    assert not ExprTransformer(data=data).transform(tree)

