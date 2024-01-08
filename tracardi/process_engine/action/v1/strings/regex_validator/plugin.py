from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result

from .model.configuration import Configuration
from .service.validator import Validator


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class RegexValidatorAction(ActionRunner):
    validator: Validator
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)
        self.validator = Validator(self.config)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        string = dot[self.config.data]
        if self.validator.check(string) is not None:
            return Result(port='valid', value=payload)
        else:
            return Result(port='invalid', value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.strings.regex_validator.plugin',
            className='RegexValidatorAction',
            inputs=["payload"],
            outputs=["valid", "invalid"],
            init={
                'validation_regex': None,
                'data': None
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="validation_regex",
                            name="Regex pattern",
                            description="Type regex pattern that will validate data.",
                            component=FormComponent(type="text", props={"label": "Regex pattern"})
                        ),
                        FormField(
                            id="data",
                            name="Path to data",
                            description="Type path to data that will be validated.",
                            component=FormComponent(type="forceDotPath", props={"defaultSourceValue": "event"})
                        )
                    ]
                ),
            ]),
            manual="regex_validator_action",
            version='0.6.0.1',
            license="MIT + CC",
            author="Patryk Migaj"

        ),
        metadata=MetaData(
            name='Regex validator',
            desc='Validates data with regex pattern',
            icon='regex',
            tags=['condition'],
            group=["Regex", "Validators"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "valid": PortDoc(desc="Returns payload if validation passed."),
                    "invalid": PortDoc(desc="Returns payload if validation did not pass."),
                }
            )
        )
    )
