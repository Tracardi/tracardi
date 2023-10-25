from collections import defaultdict

from pydantic import field_validator
from enum import Enum
import re

from tracardi.process_engine.action.v1.operations.contains_pattern.patterns import patterns
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.result import Result


class Pattern(str, Enum):
    ip = "ip"
    url = "url"
    date = "date"
    email = "email"
    all = "all"


class Config(PluginConfig):
    field: str
    pattern: Pattern

    class PatternConfig:
        use_enum_values = True

    @field_validator("field")
    @classmethod
    def validate_field(cls, value):
        if not value:
            raise ValueError("Field cannot be empty")
        return value

    @field_validator("pattern")
    @classmethod
    def validate_pattern(cls, value):
        if not value:
            raise ValueError("Pattern cannot be empty")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class WrongFieldTypeError(Exception):
    """Raised when given field has wrong data type"""
    pass


class EmptyPatternError(Exception):
    """Raised when pattern field is empty"""
    pass


class ContainsPatternAction(ActionRunner):
    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        value = dot[self.config.field]

        if not isinstance(value, str):
            raise WrongFieldTypeError(f"Given field must be an array or string type. {type(value)} given")

        if self.config.pattern == "all":
            found_matched = defaultdict(list)
            for k, v in patterns.items():
                matched = re.finditer(patterns[k], value)
                for match in matched:
                    found_matched[k].append(match.group(0))
            if found_matched:
                return Result(port='true', value=found_matched)

        elif self.config.pattern == "email":
            if re.match(patterns["email"], value):
                return Result(port="true", value={"email": [value]})

        elif self.config.pattern == "url":
            if re.match(patterns["url"], value):
                return Result(port="true", value={"url": [value]})

        elif self.config.pattern == "date":
            if re.match(patterns["date"], value):
                return Result(port="true", value={"date": [value]})

        elif self.config.pattern == "ip":
            if re.match(patterns["ip"], value):
                return Result(port="true", value={"ip": [value]})

        return Result(port="false", value={"message": "Didn't find any patterns"})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ContainsPatternAction',
            inputs=["payload"],
            outputs=["true", "false"],
            version='0.7.2',
            license="MIT + CC",
            author="Mateusz Zitaruk",
            init={
                "field": None,
                "pattern": None
            },
            manual="contains_pattern_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Field contains pattern plugin configuration",
                        fields=[
                            FormField(
                                id="field",
                                name="Type string or path to string that you want to check.",
                                component=FormComponent(
                                    type="dotPath",
                                    props={
                                        "label": "Path",
                                        "defaultSourceValue": "event"
                                    }
                                )
                            ),
                            FormField(
                                id="pattern",
                                name="Pattern",
                                description="Type pattern to check if data field contains it.",
                                component=FormComponent(
                                    type="select",
                                    props={
                                        "label": "Pattern", "items": {
                                            "all": "all",
                                            "email": "email",
                                            "url": "url",
                                            "ip": "ip",
                                            "date": "date"
                                        }
                                    }
                                )
                            )
                        ]
                    )
                ]
            )

        ),
        metadata=MetaData(
            name='Contains pattern',
            desc='Checks if field contains defined pattern.',
            icon='exists',
            group=["String"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"true": PortDoc(desc="This port returns new object if field contains defined pattern."),
                         "false":
                             PortDoc(desc="This port returns payload if field doesn't contain defined pattern.")}
            )
        )
    )
