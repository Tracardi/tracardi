import jsonschema
from tracardi.domain.storage_record import StorageRecords
from tracardi.service.cache_manager import CacheManager
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.domain.event_validator import EventValidator
from tracardi.exceptions.exception import EventValidationException
from dotty_dict import Dotty
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.parser import Parser
from typing import List, Tuple, Optional

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


def _validate_with_multiple_schemas(event: dict, validators: List[EventValidator]) -> Tuple[bool, Optional[str]]:
    dot = DotAccessor(
        profile=None,
        session=None,
        payload=None,
        event=event,
        flow=None,
        memory=None
    )

    validators_to_use = _get_validators_that_meet_condition(validators, dot)

    for validator in validators_to_use:
        error, message = _validate(validator, dot)
        if error:
            return error, message
    return False, None


async def get_event_validation_result(event: dict, validation_schemas: StorageRecords) -> Tuple[bool, Optional[str]]:
    if validation_schemas:
        return _validate_with_multiple_schemas(event, validation_schemas.to_domain_objects(EventValidator))
    return False, None
