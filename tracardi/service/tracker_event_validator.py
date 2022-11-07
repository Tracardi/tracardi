from tracardi.domain.event import Event
from tracardi.service.storage.driver import storage
from tracardi.service.notation.dot_accessor import DotAccessor
import jsonschema
from tracardi.domain.event_validator import EventValidator
from tracardi.exceptions.exception import EventValidationException
from dotty_dict import Dotty
from tracardi.process_engine.tql.transformer.expr_transformer import ExprTransformer
from tracardi.process_engine.tql.parser import Parser
from typing import List

parser = Parser(Parser.read('grammar/uql_expr.lark'), start='expr')


def validate(dot: DotAccessor, validator: EventValidator) -> bool:
    for key, val_schema in validator.validation.json_schema.items():
        if not DotAccessor.validate(key):
            raise EventValidationException(
                f"Please correct the reference to data in your validation schema. Expected dot notation got {key}")

        try:
            value = dot[key].to_dict() if isinstance(dot[key], Dotty) else dot[key]
            jsonschema.validate(value, val_schema)
        except (jsonschema.ValidationError, KeyError) as _:
            return False

    return True


def validate_with_multiple_schemas(dot: DotAccessor, validators: List[EventValidator]) -> bool:
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

    return all(validate(dot, validator) for validator in validators_to_use)


async def validate_event(event: Event, dot: DotAccessor) -> Event:
    validation_schemas = await storage.driver.event_validation.load_by_event_type(event.type)

    if validation_schemas:
        if validate_with_multiple_schemas(dot, validation_schemas) is False:
            event.metadata.valid = False
    return event
