from tracardi.config import memory_cache
from tracardi.domain.console import Console
from tracardi.domain.event import Event
from tracardi.exceptions.exception_service import get_traceback
from tracardi.service.cache_manager import CacheManager
from tracardi.service.console_log import ConsoleLog
from tracardi.service.notation.dot_accessor import DotAccessor
import jsonschema
from tracardi.domain.event_validator import EventValidator
from tracardi.exceptions.exception import EventValidationException
from dotty_dict import Dotty, dotty
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.parser import Parser
from typing import List

from tracardi.service.tracker_event_props_reshaper import EventPropsReshaper
from tracardi.service.utils.getters import get_entity_id

parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')
cache = CacheManager()


class EventsValidationHandler:

    def __init__(self, dot: DotAccessor, console_log: ConsoleLog):
        self.console_log = console_log
        self.dot = dot

    def _validate(self, validator: EventValidator) -> bool:
        for key, val_schema in validator.validation.json_schema.items():
            if not DotAccessor.validate(key):
                raise EventValidationException(
                    f"Please correct the reference to data in your validation schema. Expected dot notation got {key}")

            try:
                value = self.dot[key].to_dict() if isinstance(self.dot[key], Dotty) else self.dot[key]
                jsonschema.validate(value, val_schema)
            except jsonschema.ValidationError as e:
                self.console_log.append(
                    Console(
                        event_id=get_entity_id(self.dot.event),
                        profile_id=get_entity_id(self.dot.profile),
                        origin='tracker',
                        class_name='tracker',
                        module=__name__,
                        type='warning',
                        message=f"Validation error: {str(e)}",
                        traceback=get_traceback(e)
                    )
                )
                return False
            except KeyError as e:
                self.console_log.append(
                    Console(
                        event_id=get_entity_id(self.dot.event),
                        profile_id=get_entity_id(self.dot.profile),
                        origin='tracker',
                        class_name='tracker',
                        module=__name__,
                        type='error',
                        message=str(e),
                        traceback=get_traceback(e)
                    )
                )
                return False

        return True

    def validate_with_multiple_schemas(self, validators: List[EventValidator]) -> bool:
        validators_to_use = []
        for validator in validators:
            if validator.validation.condition:
                try:
                    condition = ExprTransformer(dot=self.dot).transform(
                        tree=parser.parse(validator.validation.condition))
                except Exception:
                    condition = False
            else:
                condition = True

            if condition:
                validators_to_use.append(validator)

        return all(self._validate(validator) for validator in validators_to_use)

    async def validate_event(self, event: Event) -> Event:
        validation_schemas = await cache.event_validation(event_type=event.type,
                                                          ttl=memory_cache.event_validation_cache_ttl)

        if validation_schemas:
            if self.validate_with_multiple_schemas(validation_schemas.to_domain_objects(EventValidator)) is False:
                event.metadata.valid = False
        return event

    async def reshape_event(self, event: Event) -> Event:
        if event.metadata.valid:
            reshape_schemas = await cache.event_reshaping(event.type, ttl=15)
            if reshape_schemas:
                resharper = EventPropsReshaper(
                    dot=self.dot,
                    event=event,
                )
                return resharper.reshape(schemas=reshape_schemas)
        return event

    async def index_event_traits(self, event: Event) -> Event:
        event_meta_data = await cache.event_metadata(event.type, ttl=memory_cache.event_metadata_cache_ttl)
        if 'index_schema' in event_meta_data:
            index_schema = event_meta_data['index_schema']
            if isinstance(index_schema, dict):
                dot_event_properties = dotty(event.properties)
                dot_event_traits = dotty(event.traits)

                for property, trait in index_schema.items():  # type: str, str
                    try:
                        if property in dot_event_properties:
                            dot_event_traits[trait] = dot_event_properties[property]
                            del dot_event_properties[property]
                        else:
                            raise KeyError(f"Property '{property}' does not exist in event {event.id}")
                    except KeyError as e:
                        console = Console(
                            origin="event-indexing",
                            event_id=event.id,
                            flow_id=None,
                            node_id=None,
                            profile_id=None,
                            module=__name__,
                            class_name=EventsValidationHandler.__name__,
                            type="warning",
                            message=str(e),
                            traceback=get_traceback(e)
                        )
                        self.console_log.append(console)

                event.properties = dot_event_properties.to_dict()
                event.traits = dot_event_traits.to_dict()
        return event

    async def validate_and_reshape_index_events(self, events) -> List[Event]:
        processed_events = []
        for event in events:

            self.dot.set_storage("event", event)

            # mutates console_log
            event = await self.validate_event(event)

            try:
                event = await self.reshape_event(event)
            except Exception as e:
                self.console_log.append(
                    Console(
                        event_id=event.id,
                        profile_id=get_entity_id(self.dot.profile),
                        origin='tracker',
                        class_name='tracker',
                        module=__name__,
                        type='error',
                        message=str(e),
                        traceback=get_traceback(e)
                    )
                )

            event = await self.index_event_traits(event)

            processed_events.append(event)

        return processed_events
