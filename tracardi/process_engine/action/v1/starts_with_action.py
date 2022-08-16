from typing import Optional


from tracardi.service.plugin.domain.config import PluginConfig

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class Config(PluginConfig):
    field: str
    defined_prefix: str


def validate(config: dict) -> Config:
    return Config(**config)


class StartsWithAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)
        self.field = self.config.field
        self.defined_prefix = self.config.defined_prefix

    async def run(self, payload: dict, in_edge=None):

        if self.field.startswith(self.defined_prefix) and self.defined_prefix != "":
            return Result(port="true", value=payload)
        else:
            self.console.error("Field doesn't starts with defined string.")
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
                "defined_prefix": "prefix"
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
                                    type="text",
                                    props={
                                        "label": "Plugin field"
                                    }
                                )
                            ),
                            FormField(
                                id="defined_prefix",
                                name="Prefix",
                                description="Type prefix to check if plugin field starts with.",
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
                             PortDoc(desc="This port returns error if field doesnt contains defined string")}
            )
        )
    )
