from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result

from .model.configuration import Configuration
from .service.operations import convert


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class StringPropertiesActions(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        string = dot[self.config.string]

        if not isinstance(string, str):
            raise ValueError("Provided string is not string it is `{}`".format(type(string)))

        return Result(port="payload", value=convert(string))


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.strings.string_operations.plugin',
            className='StringPropertiesActions',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.0.1',
            license="MIT + CC",
            author="Patryk Migaj",
            manual="string_properties_action",
            init={
                "string": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="String settings",
                    fields=[
                        FormField(
                            id="string",
                            name="Path to string",
                            description="Select source and path to string.",
                            component=FormComponent(type="forceDotPath", props={})
                        )
                    ])
            ]),
        ),
        metadata=MetaData(
            name='String properties',
            desc='Makes a string transformations like: lowercase remove spaces split and other',
            icon='uppercase',
            group=["String"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns string properties."),
                }
            )
        )
    )
