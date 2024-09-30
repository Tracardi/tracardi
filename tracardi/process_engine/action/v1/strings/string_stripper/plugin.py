from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
import re
from .model.config import Config


def validate(config: dict) -> Config:
    return Config(**config)


class StringStripper(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        string = dot[self.config.string]
        to_remove = dot[self.config.to_remove]
        return Result(port="removed", value={"value": re.sub(
            f"[{to_remove}]", "", string
        )})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=StringStripper.__name__,
            inputs=["payload"],
            outputs=["removed"],
            version='0.8.2',
            license="MIT + CC",
            author="kokobhara",
            init={
                "string": None,
                "to_remove": None,
            },
            manual="string_stripper_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="String stripper configuration",
                        fields=[
                            FormField(
                                id="string",
                                name="String",
                                description="Please provide a path to the text (or the text itself) that you want to "
                                            "remove characters from.",
                                component=FormComponent(type="dotPath", props={"label": "String"})
                            ),
                            FormField(
                                id="to_remove",
                                name="To remove",
                                description="Please provide the text containing only of the characters you wish to remove.",
                                component=FormComponent(type="text", props={"label": "Characters to remove"})
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='String stripper',
            desc='Removes all defined characters from a string string.',
            icon='uppercase',
            group=["String"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object."),
                },
                outputs={
                    "payload": PortDoc(desc="This port returns string after removing the provided characters."),
                },
            )
        )
    )
