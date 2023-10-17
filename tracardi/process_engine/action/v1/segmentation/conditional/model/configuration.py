from pydantic import field_validator, validator
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    condition: str
    true_action: str = 'add'
    false_action: str = 'remove'
    true_segment: str
    false_segment: str

    @field_validator("condition")
    @classmethod
    def is_valid_condition(cls, value):
        _condition = Condition()
        try:
            _condition.parse(value)
        except Exception as e:
            raise ValueError(str(e))

        return value

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("true_segment")
    def is_valid_true_segment(cls, value, values):
        if 'true_action' in values and values['true_action'] != 'none':
            if value == "":
                raise ValueError("Segment can not be empty for action {}".format(values['true_action']))
        return value

    # TODO[pydantic]: We couldn't refactor the `validator`, please replace it by `field_validator` manually.
    # Check https://docs.pydantic.dev/dev-v2/migration/#changes-to-validators for more information.
    @validator("false_segment")
    def is_valid_false_segment(cls, value, values):
        if 'false_action' in values and values['false_action'] != 'none':
            if value == "":
                raise ValueError("Segment can not be empty for action {}".format(values['false_action']))
        return value
