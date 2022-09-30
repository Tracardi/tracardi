from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event import Event
from tracardi.domain.event_payload_validator import ReshapeSchema
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.parser import Parser


class EventPropsReshapingError(Exception):
    pass


class EventPropsReshaper:
    parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')

    def __init__(self, dot: DotAccessor, event: Event):
        self.event = event
        self.dot = dot

    def reshape(self, schema: ReshapeSchema) -> Event:
        try:
            condition = ExprTransformer(dot=self.dot).transform(tree=self.parser.parse(schema.condition))
        except Exception:
            condition = False

        if schema.template is None or (schema.condition is not None and condition is False):
            return self.event

        try:
            props = DictTraverser(dot=self.dot, include_none=True, default=None).reshape(
                schema.template
            )

        except Exception as e:
            raise EventPropsReshapingError(f"Could not reshape event properties due to an error: `{str(e)}`")

        else:
            return Event(**self.event.dict(exclude={"properties"}), properties=props)
