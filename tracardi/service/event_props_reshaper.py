from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event import Event
from tracardi.domain.event_payload_validator import ReshapeSchema
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.parser import Parser
from tracardi.process_engine.tql.condition import Condition
from tracardi.domain.event import RESHAPED


class EventPropsReshapingError(Exception):
    pass


class EventPropsReshaper:
    parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')

    def __init__(self, dot: DotAccessor, event: Event):
        self.event = event
        self.dot = dot

    def reshape(self, schema: ReshapeSchema) -> None:
        if schema.template is None or (schema.condition is not None and ExprTransformer(dot=self.dot).transform(
                tree=self.parser.parse(schema.condition)
        ) is False):
            return

        try:
            self.event.properties = DictTraverser(dot=self.dot, include_none=True, default=None).reshape(
                schema.template
            )

        except Exception as e:
            raise EventPropsReshapingError(f"Could not reshape event properties due to an error: `{str(e)}`")

        else:
            self.event.metadata.status = RESHAPED
