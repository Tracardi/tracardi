from tracardi.process_engine.action.v1.flow.property_exists.model.configuration import Configuration
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


def validate(config: dict):
    return Configuration(**config)


class PropertyExistsAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        if self.config.property in dot and dot[self.config.property] is not None:
            if isinstance(dot[self.config.property], str):
                if dot[self.config.property] == "":
                    return Result(port="false", value=payload)

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
            version="0.8.0",
            init={
                'property': 'profile@data.contact.email.main'
            },
            manual="data_exists_action",
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="property",
                            name="Data property to check",
                            description="Type data to validate if exists and not empty.",
                            component=FormComponent(type="dotPath", props={
                                "defaultSourceValue": "event",
                                "defaultMode": 1
                            })
                        ),
                    ]
                ),
            ])
        ),
        metadata=MetaData(
            name='Data exists',
            desc='Checks if the data property exists and is not null or empty.',
            icon='exists',
            type="condNode",
            group=["Flow control"],
            tags=['condition'],
            purpose=['collection', 'segmentation'],
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
