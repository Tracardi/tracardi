from pydantic import BaseModel, validator
from tracardi.process_engine.tql.condition import Condition


class Configuration(BaseModel):
    condition: str
    true_action: str = 'add'
    false_action: str = 'remove'
    true_segment: str
    false_segment: str

    @validator("condition")
    def is_valid_condition(cls, value):
        _condition = Condition()
        try:
            _condition.parse(value)
        except Exception as e:
            raise ValueError(str(e))

        return value

    @validator("true_segment")
    def is_valid_true_segment(cls, value, values):
        if 'true_action' in values and values['true_action'] != 'none':
            if value == "":
                raise ValueError("Segment can not be empty for action {}".format(values['true_action']))
        return value

    @validator("false_segment")
    def is_valid_false_segment(cls, value, values):
        if 'false_action' in values and values['false_action'] != 'none':
            if value == "":
                raise ValueError("Segment can not be empty for action {}".format(values['false_action']))
        return value
