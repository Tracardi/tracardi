from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.service.notation.dict_traverser import DictTraverser
from typing import List, Tuple, Optional


class EventDataReshaper:

    def __init__(self, dot: DotAccessor):
        self.dot = dot

    def _reshape(self, schema: dict):
        return DictTraverser(dot=self.dot, include_none=True, default=None).reshape(
            schema
        )

    def reshape(self, schemas: List[EventReshapingSchema]) -> Optional[Tuple[dict, dict, Optional[dict]]]:

        """
        Returns event and session context
        """

        event_properties: dict = {}
        event_context: dict = {}
        session_context = None
        for schema in schemas:

            # ALERT: Return first reshaped event, no multiple reshapes available

            reshaped = False
            if schema.reshaping.reshape_schema.has_event_reshapes():
                reshaped = True

                if schema.reshaping.reshape_schema.properties:
                    event_properties = self._reshape(schema.reshaping.reshape_schema.properties)

                if schema.reshaping.reshape_schema.context:
                    event_context = self._reshape(schema.reshaping.reshape_schema.context)

            if schema.reshaping.reshape_schema.has_session_reshapes():
                if schema.reshaping.reshape_schema.session:
                    reshaped = True
                    session_context = self._reshape(schema.reshaping.reshape_schema.session)

            if reshaped:
                return event_properties, event_context, session_context

        return None
