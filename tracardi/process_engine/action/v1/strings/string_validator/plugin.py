from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi_plugin_sdk.domain.result import Result

from .model.configuration import Configuration
from .service.validator import Validator


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class StringValidatorAction(ActionRunner):
    def __init__(self, **kwargs):
        self.config = validate(kwargs)
        self.validator = Validator(self.config)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        string = dot[self.config.data]

        if self.validator.check(string):
            return Result(port='valid', value=payload), Result(port='invalid', value=None)
        else:
            return Result(port='valid', value=None), Result(port='invalid', value=payload)


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
            license="MIT",
            author="Patryk Migaj, Risto Kowaczewski"

        ),
        metadata=MetaData(
            name='Data validator',
            desc='Validates data such as: email, url, ipv4, date, time,int,float, phone number, ean code',
            type='flowNode',
            width=300,
            height=100,
            icon='ok',
            group=["Validators"],
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
