from tracardi_dot_notation.dot_accessor import DotAccessor

from ...domain.context import Context
from ...domain.event import Event
from ...domain.flow import Flow
from ...domain.profile import Profile
from ...domain.session import Session
from ...domain.source import Source
from ...process_engine.tql.parser import Parser
from ...process_engine.tql.transformer.expr_transformer import ExprTransformer
from ...process_engine.tql.utils.dictonary import flatten

payload = {
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

profile = Profile(id="1")
session = Session(id="2")
source = Source(id="3", type="event")
context = Context()
event = Event(id="event-id", type="type", source=source, context=context, profile=profile, session=session)
flow = Flow(id="flow-id", name="flow")
dot = DotAccessor(profile, session, payload, event, flow)

parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')


def test_tql_operations():
    tree = parser.parse("payload@a.d.aa between 1 and 2")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.e == \"test\"")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b == payload@a.f")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.g == True")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.h == null")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b == 1")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b >= 1")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b <= 1")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b > 0")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b < 2")
    assert ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("datetime(payload@a.i) == datetime(\"2021-01-10\")")
    # assert ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("datetime(payload@a.i) <= datetime(\"2021-01-10\")")
    # assert ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("datetime(payload@a.i) >= datetime(\"2021-01-10\")")
    # assert ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("datetime(payload@a.i) < datetime(\"2021-01-11\")")
    # assert ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("datetime(payload@a.i) > datetime(\"2021-01-09\")")
    # assert ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("datetime(payload@a.i) < datetime(\"2021-01-10 00:00:01\")")
    # assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.h is null")
    assert ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("datetime(payload@a.i) between datetime(\"2020-01-01\") and datetime(\"2022-01-01\")")
    # assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.h exists")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.h.h not exists")
    assert ExprTransformer(dot=dot).transform(tree)


def test_tql_false_operations():
    tree = parser.parse("payload@a.d.aa between 3 and 4")
    assert not ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.e != \"test\"")
    assert not ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b != payload@a.f")
    assert not ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.g != True")
    assert not ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.h != null")
    assert not ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b != 1")
    assert not ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b > 1")
    assert not ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b < 1")
    assert not ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b > 0")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.b > 2")
    assert not ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("datetime(payload@a.i) != datetime(\"2021-01-10\")")
    # assert not ExprTransformer(dot=dot).transform(tree)
    #
    # tree = parser.parse("datetime(a.i) < datetime(\"2021-01-10\")")
    # assert not ExprTransformer(dot=dot).transform(tree)
    #
    # tree = parser.parse("datetime(a.i) > datetime(\"2021-01-10\")")
    # assert not ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("datetime(a.i) > datetime(\"2021-01-11\")")
    # assert not ExprTransformer(dot=dot).transform(tree)
    #
    # tree = parser.parse("datetime(a.i) < datetime(\"2021-01-09\")")
    # assert not ExprTransformer(dot=dot).transform(tree)
    #
    # tree = parser.parse("datetime(a.i) > datetime(\"2021-01-10 00:00:01\")")
    # assert not ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.h != null")
    assert not ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("datetime(a.i) between datetime(\"2022-01-01\") and datetime(\"2023-01-01\")")
    # assert not ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("payload@a.h not exists")
    # assert not ExprTransformer(dot=dot).transform(tree)

    # tree = parser.parse("payload@a.h.h exists")
    # assert not ExprTransformer(dot=dot).transform(tree)


def test_tql_bool_operations():
    tree = parser.parse("payload@a.d.aa between 1 and 2 and payload@a.e == \"test\"")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.d.aa between 1 and 2 or payload@a.e != \"test\"")
    assert ExprTransformer(dot=dot).transform(tree)

    tree = parser.parse("payload@a.d.aa between 2 and 3 and payload@a.e != \"test\"")
    assert not ExprTransformer(dot=dot).transform(tree)

