from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result

from .model.configuration import Configuration
from .service.validator import Validator


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class StringValidatorAction(ActionRunner):
    validator: Validator
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)
        self.validator = Validator(self.config)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        string = dot[self.config.data]

        if self.validator.check(string):
            return Result(port='valid', value=payload)
        else:
            return Result(port='invalid', value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.strings.string_validator.plugin',
            className='StringValidatorAction',
            inputs=["payload"],
            outputs=["valid", "invalid"],
            init={
                'validator': None,
                'data': None
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="validator",
                            name="Validation type",
                            description="Select the kind of validation you would like to perform.",
                            component=FormComponent(
                                type="select",
                                props={
                                    "label": "Validate as", "items": {
                                        'email': 'E-mail',
                                        'url': 'URL',
                                        'ipv4': 'IP Address',
                                        'date': 'Date',
                                        'time': 'Time',
                                        'int': 'Integer Number',
                                        'float': 'Float number',
                                        'number_phone': 'Phone number'
                                    }
                                }
                            )
                        )
                    ]
                ),
                FormGroup(
                    fields=[
                        FormField(
                            id="data",
                            name="Path to data",
                            description="Type path to data to be validated.",
                            component=FormComponent(
                                type="forceDotPath",
                                props={
                                    "defaultSourceValue": "event"
                                })
                        )
                    ]

                ),
            ]),
            manual="string_validator_action",
            version='0.6.0.1',
            license="MIT + CC",
            author="Patryk Migaj, Risto Kowaczewski"

        ),
        metadata=MetaData(
            name='Data validator',
            desc='Validates data such as: email, url, ipv4, date, time,int,float, phone number, ean code',
            icon='ok',
            group=["String"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                },
                outputs={
                    "valid": PortDoc(desc="Returns payload if the validation passed."),
                    "invalid": PortDoc(desc="Returns payload if the validation did not pass."),
                }
            )
        )
    )
