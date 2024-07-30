from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.service.notation.dict_traverser import DictTraverser
from typing import List, Tuple, Optional


class EventDataReshaper:

    def __init__(self, dot: DotAccessor):
        self.dot = dot

    def _reshape(self, schema: dict) -> dict:
        return DictTraverser(dot=self.dot, include_none=True, default=None).reshape(
            schema
        )

    @staticmethod
    def _has_delete_schema(reshape_schema) -> bool:
        return '-' in reshape_schema.properties and isinstance(reshape_schema.properties['-'], list)

    @staticmethod
    def _get_delete_schema(reshape_schema) -> List[str]:
        return reshape_schema.properties['-']

    def reshape(self, schemas: List[EventReshapingSchema]) -> Optional[Tuple[dict, dict, Optional[dict]]]:

        """
        Returns event and session context.
        """

        event_properties = None
        event_context = None
        session_context = None
        for schema in schemas:

            # ALERT: Return first reshaped event, no multiple reshapes available

            reshaped = False
            if schema.reshaping.reshape_schema.has_event_reshapes():
                reshaped = True

                if schema.reshaping.reshape_schema.properties:

                    # Delete event properties
                    delete_schema = None
                    if 'properties' in self.dot.event and self._has_delete_schema(schema.reshaping.reshape_schema):
                        delete_schema = schema.reshaping.reshape_schema.properties['-']
                        del schema.reshaping.reshape_schema.properties['-']

                    # If after removing the '-' there is no reshapes. Do not change the properties
                    # (reassign original properties)
                    if not schema.reshaping.reshape_schema.properties and 'properties' in self.dot.event:
                        # If not reshape define for event return default properties
                        event_properties = dict(self.dot.event['properties'])
                    else:
                        # Reshape properties
                        event_properties = self._reshape(schema.reshaping.reshape_schema.properties)

                    # Remove properties
                    if delete_schema and event_properties:
                        for event_property in delete_schema:
                            # Remove that value
                            event_properties.pop(event_property, None)

                if schema.reshaping.reshape_schema.context:
                    event_context = self._reshape(schema.reshaping.reshape_schema.context)

            if schema.reshaping.reshape_schema.has_session_reshapes():
                if schema.reshaping.reshape_schema.session:
                    reshaped = True
                    session_context = self._reshape(schema.reshaping.reshape_schema.session)

            if reshaped:
                return event_properties, event_context, session_context

        return None
