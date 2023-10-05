import jsonschema

from tracardi.domain.payload.event_payload import ProcessStatus
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.storage_record import StorageRecords
from tracardi.service.cache_manager import CacheManager
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event_validator import EventValidator
from tracardi.exceptions.exception import EventValidationException
from dotty_dict import Dotty
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.parser import Parser
from typing import Tuple, Optional
from tracardi.config import memory_cache

parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')
cache = CacheManager()


def _validate(validator: EventValidator, dot: DotAccessor) -> Tuple[bool, Optional[str]]:
    for key, val_schema in validator.validation.json_schema.items():
        if not DotAccessor.validate(key):
            raise EventValidationException(
                f"Please correct the reference to data in your validation schema. Expected dot notation got {key}")

        try:
            value = dot[key].to_dict() if isinstance(dot[key], Dotty) else dot[key]
            jsonschema.validate(value, val_schema)
        except jsonschema.ValidationError as e:
            return True, str(e)
        except KeyError as e:
            return True, str(e)

    return False, None


def _get_validators_that_meet_condition(validators, dot: DotAccessor):
    validators_to_use = []
    for validator in validators:
        if validator.validation.condition:
            try:
                condition = ExprTransformer(dot=dot).transform(
                    tree=parser.parse(validator.validation.condition))
            except Exception:
                condition = False
        else:
            condition = True

        if condition:
            validators_to_use.append(validator)

    return validators_to_use


async def _get_event_validation_result(event: dict, validation_schemas: StorageRecords) -> Tuple[bool, Optional[str]]:
    if validation_schemas:

        dot = DotAccessor(
            profile=None,
            session=None,
            payload=None,
            event=event,
            flow=None,
            memory=None
        )

        validators = validation_schemas.to_domain_objects(EventValidator)

        validators_to_use = _get_validators_that_meet_condition(validators, dot)

        for validator in validators_to_use:
            error, message = _validate(validator, dot)
            if error:
                return error, message
        return False, None

    return False, None


async def validate_events(tracker_payload: TrackerPayload) -> TrackerPayload:

    """
    Mutates the tracker payload and ads ProcessStatus to events.
    """

    for event_payload in tracker_payload.events:
        validation_schemas = await cache.event_validation(
            event_type=event_payload.type,
            ttl=memory_cache.event_validation_cache_ttl)
        validation_error, error_message = await _get_event_validation_result(event_payload.to_event_dict(
            tracker_payload.source,
            tracker_payload.session,
            tracker_payload.profile,
            not tracker_payload.profile_less
        ), validation_schemas)

        event_payload.validation = ProcessStatus(error=validation_error, message=error_message)

    return tracker_payload
