from tracardi.service.notation.dot_accessor import DotAccessor
import jsonschema
from tracardi.domain.event_payload_validator import EventTypeManager
from tracardi.exceptions.exception import EventValidationException
from dotty_dict import Dotty


def validate(dot: DotAccessor, validator: EventTypeManager) -> None:
    for key, val_schema in validator.validation.json_schema.items():
        if not DotAccessor.validate(key):
            raise EventValidationException(
                f"Please correct the reference to data in your validation schema. Expected dot notation got {key}")

        try:
            value = dot[key].to_dict() if isinstance(dot[key], Dotty) else dot[key]
            jsonschema.validate(value, val_schema)
        except (jsonschema.ValidationError, KeyError) as e:
            raise EventValidationException("{}: {}".format(key, str(e)))
