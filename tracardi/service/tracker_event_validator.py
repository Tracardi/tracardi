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
from dotty_dict import Dotty
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.parser import Parser
from typing import List

from tracardi.service.utils.getters import get_entity_id

parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')
cache = CacheManager()


def validate(dot: DotAccessor, validator: EventValidator, console_log: ConsoleLog) -> bool:
    for key, val_schema in validator.validation.json_schema.items():
        if not DotAccessor.validate(key):
            raise EventValidationException(
                f"Please correct the reference to data in your validation schema. Expected dot notation got {key}")

        try:
            value = dot[key].to_dict() if isinstance(dot[key], Dotty) else dot[key]
            jsonschema.validate(value, val_schema)
        except jsonschema.ValidationError as e:
            console_log.append(
                Console(
                    event_id=dot.event.id,
                    profile_id=get_entity_id(dot.profile),
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
            console_log.append(
                Console(
                    event_id=dot.event.id,
                    profile_id=get_entity_id(dot.profile),
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


def validate_with_multiple_schemas(dot: DotAccessor, validators: List[EventValidator], console_log: ConsoleLog) -> bool:
    validators_to_use = []
    for validator in validators:
        if validator.validation.condition:
            try:
                condition = ExprTransformer(dot=dot).transform(tree=parser.parse(validator.validation.condition))
            except Exception:
                condition = False
        else:
            condition = True

        if condition:
            validators_to_use.append(validator)

    return all(validate(dot, validator, console_log) for validator in validators_to_use)


async def validate_event(event: Event, dot: DotAccessor, console_log: ConsoleLog) -> Event:
    validation_schemas = await cache.event_validation(event_type=event.type,
                                                      ttl=memory_cache.event_validation_cache_ttl)

    if validation_schemas:
        if validate_with_multiple_schemas(
                dot,
                validation_schemas.to_domain_objects(EventValidator),
                console_log
        ) is False:
            event.metadata.valid = False
    return event
