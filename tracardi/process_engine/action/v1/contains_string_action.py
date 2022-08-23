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


class ContainsStringAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        if self.config.prefix in dot[self.config.field]:
            return Result(port="true", value=payload)
        else:
            return Result(port="false", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ContainsStringAction',
            inputs=["payload"],
            outputs=["true", "false"],
            version='0.7.2',
            license="MIT",
            author="Mateusz Zitaruk",
            init={
                "field": "",
                "prefix": ""
            },
            manual="contains_string_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Field contains string plugin configuration",
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
                                description="Type prefix to check if data field contains it.",
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
            name='Contain string',
            desc='Checks if field contains defined string.',
            icon='question',
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
