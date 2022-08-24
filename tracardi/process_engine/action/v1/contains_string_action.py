from pydantic import validator

from tracardi.service.plugin.domain.config import PluginConfig

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class Config(PluginConfig):
    field: str
    substring: str

    @validator("substring")
    def validate_prefix(cls, value):
        if value == "":
            raise ValueError("Substring cannot be empty")
        return value

    @validator("field")
    def validate_field(cls, value):
        if value == "":
            raise ValueError("Field cannot be empty")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class WrongFieldTypeError(Exception):
    """Raised when given field has wrong data type"""
    pass


class ContainsStringAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        value = dot[self.config.field]

        if not isinstance(value, str) or isinstance(value, list):
            raise WrongFieldTypeError(f"Given field must be an array or string type. {type(value)} given")

        if self.config.substring in value:
            return Result(port="true", value=payload)

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
                "field": None,
                "substring": None
            },
            manual="contains_string_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Field contains string plugin configuration",
                        fields=[
                            FormField(
                                id="field",
                                name="Type string or path to string that you want to check.",
                                component=FormComponent(
                                    type="dotPath",
                                    props={
                                        "label": "Path",
                                        "defaultSourceValue": "event"
                                    }
                                )
                            ),
                            FormField(
                                id="substring",
                                name="Substring",
                                description="Type prefix to check if data field contains it.",
                                component=FormComponent(
                                    type="text",
                                    props={
                                        "label": "Substring"
                                    }
                                )
                            )
                        ]
                    )
                ]
            )

        ),
        metadata=MetaData(
            name='Contains string',
            desc='Checks if field contains defined string.',
            icon='question',
            group=["Flow control"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"true": PortDoc(desc="This port returns payload if field contains defined substring."),
                         "false":
                             PortDoc(desc="This port returns payload if field doesnt contain defined substring")}
            )
        )
    )
