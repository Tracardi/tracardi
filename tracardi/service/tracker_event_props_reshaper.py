from tracardi.domain.entity import Entity
from tracardi.domain.session import Session
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event import Event
from tracardi.domain.event_reshaping_schema import EventReshapingSchema, EventReshapeDefinition
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.parser import Parser
from typing import List, Tuple, Optional


class Conditions(List[Tuple[bool, EventReshapingSchema]]):

    def is_valid(self):
        counter = 0
        for condition, _ in self:
            if condition:
                counter += 1
            if counter > 1:
                break

        return counter < 2


class EventDataReshaper:

    parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')

    def __init__(self, dot: DotAccessor, event: Event, session: Session):
        self.session = session
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

    def _reshape(self, schema: dict):
        return DictTraverser(dot=self.dot, include_none=True, default=None).reshape(
            schema
        )

    def reshape(self, schemas: List[EventReshapingSchema]) -> Tuple[Event, Optional[Session]]:

        conditions = self._validate(schemas)

        if not conditions.is_valid():
            message = f"More than one reshaping schema condition was evaluated to true. There is no way " \
                      f"to determine which one should be used. Please correct your event reshaping setup " \
                      f"for type {self.event.type}"
            raise ValueError(message)

        event = self.event
        session = self.session
        for condition, schema in conditions:
            # Return first reshaped event
            if condition:

                if schema.reshaping.reshape_schema.has_event_reshapes():

                    event = Event(**self.event.dict())

                    if schema.reshaping.reshape_schema.properties:
                        event.properties = self._reshape(schema.reshaping.reshape_schema.properties)

                    if schema.reshaping.reshape_schema.context:
                        event.context = self._reshape(schema.reshaping.reshape_schema.context)

                if schema.reshaping.reshape_schema.has_session_reshapes():
                    session = Session(**self.session.dict())
                    if schema.reshaping.reshape_schema.session:
                        session.context = self._reshape(schema.reshaping.reshape_schema.session)

                if schema.reshaping.has_mapping():
                    if schema.reshaping.mapping.event_type:
                        event.type = schema.reshaping.mapping.event_type

                    if schema.reshaping.mapping.profile:
                        # todo read value
                        event.profile = Entity(id=schema.reshaping.mapping.profile.id)

                    if schema.reshaping.mapping.session:
                        # todo read value
                        event.session = Entity(id=schema.reshaping.mapping.session.id)

                return event, session

        return event, session
