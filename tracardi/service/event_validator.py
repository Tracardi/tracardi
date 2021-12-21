from tracardi_dot_notation.dot_accessor import DotAccessor
import jsonschema
from tracardi.domain.event_payload_validator import EventPayloadValidator
from tracardi.exceptions.exception import EventValidationException


def validate(dot: DotAccessor, validator: EventPayloadValidator) -> None:
    for key, val_schema in validator.validation.items():
        try:
            jsonschema.validate(dot[key], val_schema)
        except (jsonschema.ValidationError, KeyError) as e:
            raise EventValidationException("{}: {}".format(key, str(e)))
