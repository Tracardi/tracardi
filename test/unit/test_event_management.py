from tracardi.domain.event_payload_validator import EventTypeManager, ValidationSchema
from tracardi.service.event_validator import validate
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.exceptions.exception import EventValidationException


def test_should_read_the_whole_object():
    dot = DotAccessor(payload={"test": 1})
    validator = EventTypeManager(
        validation=ValidationSchema(json_schema={"payload@...": {"type": "object"}}, enabled=True),
        event_type="page-view",
        name="test"
    )

    # todo this validation should pass

    validate(dot, validator)


def test_should_read_the_part_of_object():
    dot = DotAccessor(payload={"test": {"a": 1}})
    validator = EventTypeManager(
        validation=ValidationSchema(json_schema={"payload@test": {"type": "object"}}, enabled=True),
        event_type="page-view",
        name="test",
    )

    try:
        validate(dot, validator)
    except Exception:
        assert False


def test_should_differentiate_types():
    dot = DotAccessor(payload={"list": ["a", "b", "c"]})
    validator = EventTypeManager(
        validation=ValidationSchema(json_schema={"payload@list": {"type": "array"}}, enabled=True),
        event_type="page-view",
        name="test"
    )

    try:
        validate(dot, validator)
    except Exception:
        assert False

    dot = DotAccessor(payload={"list": "not_a_list_for_sure"})

    try:
        validate(dot, validator)
    except EventValidationException:
        assert True


def test_should_not_pass_due_to_invalid_schema():
    dot = DotAccessor(payload={"list": ["a", "b", "c"]})
    validator = EventTypeManager(
        validation=ValidationSchema(json_schema={
            "email": {
                "type": "string"
            }
        }, enabled=True),
        event_type="page-view",
        name="test",

    )

    try:
        validate(dot, validator)
        assert False
    except EventValidationException:
        assert True
