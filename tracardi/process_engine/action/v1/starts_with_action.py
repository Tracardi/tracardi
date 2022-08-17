from typing import Optional

from pydantic import validator

from tracardi.service.plugin.domain.config import PluginConfig

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class Config(PluginConfig):
    field: str
    prefix: str

    @validator("prefix")
    def if_prefix_is_empty(cls, value):
        if value == "":
            raise ValueError("Prefix cannot be empty")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class StartsWithAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)
        self.prefix = self.config.prefix

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        if dot[self.config.field].startswith(self.prefix):
            return Result(port="true", value=payload)
        else:
            return Result(port="false", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='StartsWithAction',
            inputs=["payload"],
            outputs=["true", "false"],
            version='0.7.1',
            license="MIT",
            author="Mateusz Zitaruk",
            init={
                "field": "payload@field",
                "prefix": ""
            },
            manual="starts_with_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Starts with plugin configuration",
                        fields=[
                            FormField(
                                id="field",
                                name="Type string which you want to check.",
                                component=FormComponent(
                                    type="dotPath",
                                    props={
                                        "label": "Payload field"
                                    }
                                )
                            ),
                            FormField(
                                id="prefix",
                                name="Prefix",
                                description="Type prefix to check if payload field starts with.",
                                component=FormComponent(
                                    type="text",
                                    props={
                                        "label": "Prefix"
                                    }
                                )
                            )
                        ]
                    )
                ]
            )

        ),
        metadata=MetaData(
            name='StartsWith',
            desc='Checks if string starts with defined prefix.',
            icon='global',
            group=["Flow control"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"true": PortDoc(desc="This port returns payload if field contains defined string."),
                         "false":
                             PortDoc(desc="This port returns payload if field doesnt contains defined string")}
            )
        )
    )
