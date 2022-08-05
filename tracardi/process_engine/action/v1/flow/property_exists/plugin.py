from tracardi.process_engine.action.v1.flow.property_exists.model.configuration import Configuration
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


def validate(config: dict):
    return Configuration(**config)


class PropertyExistsAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        if self.config.property in dot:
            return Result(port="true", value=payload)

        return Result(port="false", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='PropertyExistsAction',
            author="Risto Kowaczewski",
            inputs=["payload"],
            outputs=["true", "false"],
            version="0.6.2",
            init={
                'property': 'event@context.page.url'
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="property",
                            name="Data property to check",
                            description="Type data to validate if exists.",
                            component=FormComponent(type="dotPath", props={
                                "defaultSourceValue": "event",
                                "defaultMode": 1
                            })
                        ),
                    ]
                ),
            ]),
            manual=None
        ),
        metadata=MetaData(
            name='Data exists',
            desc='Checks if the data property exists and is not null.',
            icon='exists',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload object.")
                },
                outputs={
                    "true": PortDoc(desc="This port is triggered with input payload if data property exists."),
                    "false": PortDoc(desc="This port is triggered with input payload if data property does not exist.")
                }
            )
        )
    )
