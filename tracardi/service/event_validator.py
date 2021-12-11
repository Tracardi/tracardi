from tracardi_dot_notation.dot_accessor import DotAccessor
import jsonschema
from tracardi.domain.event_payload_validator import EventPayloadValidator
from tracardi.exceptions.exception import EventValidationException


def validate(dot: DotAccessor, schema: EventPayloadValidator) -> None:
    for key, val_schema in schema.to_validate.items():
        try:
            jsonschema.validate(dot[key], val_schema)
        except jsonschema.ValidationError as e:
            raise EventValidationException(str(e))
        except KeyError as e:
            raise EventValidationException(str(e))
