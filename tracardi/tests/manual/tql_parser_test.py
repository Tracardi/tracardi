from pprint import pprint

from tracardi_dot_notation.dot_accessor import DotAccessor

from tracardi.domain.context import Context
from tracardi.domain.event import Event
from tracardi.domain.flow import Flow
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.source import Source
from tracardi.process_engine.tql.parser import Parser
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.utils.dictonary import flatten

if __name__ == "__main__":

    data = {
        "n": 1,
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
    # t = p.parse("profile@id == \"1\"")
    # t = p.parse("payload@a.h exists")
    # t = p.parse("payload@a.h == 1")
    t = p.parse("payload@n == 1")
    # pprint(t)

    profile = Profile(id="1")
    session = Session(id="2")
    payload = data
    source = Source(id="3", type="event")
    context = Context()
    event = Event(id="event-id", type="type", source=source, context=context, profile=profile, session=session)
    flow = Flow(id="flow-id", name="flow")
    dot = DotAccessor(profile, session, payload, event, flow)

    query = ExprTransformer(dot=dot).transform(t)
    pprint(query)
    # print(data)