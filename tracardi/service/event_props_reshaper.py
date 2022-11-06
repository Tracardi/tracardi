from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event import Event
from tracardi.domain.event_reshaping_schema import EventReshapingSchema, ReshapeSchema
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.parser import Parser
from typing import List


class EventPropsReshapingError(Exception):
    pass


class EventPropsReshaper:
    parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')

    def __init__(self, dot: DotAccessor, event: Event):
        self.event = event
        self.dot = dot

    def reshape(self, schemas: List[EventReshapingSchema]) -> Event:
        result = None
        for schema in schemas:
            if schema.reshaping.condition:
                try:
                    condition = ExprTransformer(dot=self.dot).transform(tree=self.parser.parse(
                        schema.reshaping.condition
                    ))
                except Exception as _:
                    condition = False

            else:
                condition = True

            if condition is False:
                continue

            if result is None:
                result = self._reshape_with_schema(schema.reshaping)
            else:
                raise EventPropsReshapingError(
                    "More than one reshaping schema condition was evaluated to true. There is no way to determine which"                       
                    f" one should be used. Please correct your event reshaping setup for type {self.event.type}"
                )

        return result if result is not None else self.event

    def _reshape_with_schema(self, schema: ReshapeSchema):
        try:
            props = DictTraverser(dot=self.dot, include_none=True, default=None).reshape(
                schema.reshape_schema
            )

        except Exception as e:
            raise EventPropsReshapingError(f"Could not reshape event properties due to an error: `{str(e)}`")

        else:
            return Event(**self.event.dict(exclude={"properties"}), properties=props)
