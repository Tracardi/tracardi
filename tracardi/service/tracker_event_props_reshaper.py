from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event import Event
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.parser import Parser
from typing import List


class Conditions(list):

    def is_valid(self):
        counter = 0
        for condition, _ in self:
            if condition:
                counter += 1
            if counter > 1:
                break

        return counter < 2


class EventPropsReshaper:

    parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')

    def __init__(self, dot: DotAccessor, event: Event):
        self.event = event
        self.dot = dot

    def _validate(self, schemas: List[EventReshapingSchema]) -> Conditions:
        conditions = Conditions()
        for schema in schemas:

            if schema.reshaping.condition is None or not schema.reshaping.condition.strip():
                conditions.append((True, schema))
            else:
                condition = ExprTransformer(dot=self.dot).transform(
                    tree=self.parser.parse(
                        schema.reshaping.condition
                    ))

                conditions.append((condition, schema))

        return conditions

    def reshape(self, schemas: List[EventReshapingSchema]) -> Event:

        conditions = self._validate(schemas)

        if not conditions.is_valid():
            message = f"More than one reshaping schema condition was evaluated to true. There is no way " \
                      f"to determine which one should be used. Please correct your event reshaping setup " \
                      f"for type {self.event.type}"
            raise ValueError(message)

        for condition, schema in conditions:
            if condition:
                props = DictTraverser(dot=self.dot, include_none=True, default=None).reshape(
                    schema.reshaping.reshape_schema
                )
                return Event(**self.event.dict(exclude={"properties"}), properties=props)

        return self.event
