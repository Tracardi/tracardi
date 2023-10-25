from pydantic import field_validator

from tracardi.service.plugin.domain.config import PluginConfig

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class Config(PluginConfig):
    field: str
    prefix: str

    @field_validator("prefix")
    @classmethod
    def if_prefix_is_empty(cls, value):
        if value == "":
            raise ValueError("Prefix cannot be empty")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class StartsWithAction(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)

        if self.config.field not in dot:
            self.console.warning(f"Field {self.config.field} does not exist.")

            return Result(port="false", value=payload)

        if dot[self.config.field].startswith(self.config.prefix):
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
            version='0.7.2',
            license="MIT + CC",
            author="Mateusz Zitaruk",
            init={
                "field": "",
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
                                name="Type string or reference to string which you want to check.",
                                component=FormComponent(
                                    type="dotPath",
                                    props={
                                        "label": "Payload field",
                                        "defaultSourceValue": "event"
                                    }
                                )
                            ),
                            FormField(
                                id="prefix",
                                name="Prefix",
                                description="Type prefix to check if data field starts with it.",
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
            name='Starts with',
            desc='Checks if string starts with defined prefix.',
            icon='exists',
            group=["String"],
            tags=['string'],
            purpose=['collection', 'segmentation'],
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
