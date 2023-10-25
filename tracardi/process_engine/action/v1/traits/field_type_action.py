from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.result import Result


class Config(PluginConfig):
    field: str


def validate(config: dict) -> Config:
    return Config(**config)


class FieldTypeAction(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        value = dot[self.config.field]

        value_type = {
            list: "array",
            str: "string",
            int: "int",
            float: "float",
            None: "null",
            dict: "object"
        }.get(type(value) if value is not None else None, str(type(value)))

        value_length = len(value) if hasattr(value, "__len__") else None

        return Result(port="field_info", value={"type": value_type, "length": value_length})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='FieldTypeAction',
            inputs=["payload"],
            outputs=["field_info"],
            version='0.7.1',
            license="MIT + CC",
            author="Dawid Kruk",
            init={
                "field": None
            },
            manual="field_type_action",
            form=Form(groups=[FormGroup(fields=[
                FormField(
                    id="field",
                    name="Reference to data field",
                    description="Please type a path to the field that you want to get information about type.",
                    component=FormComponent(type="dotPath", props={"label": "Path", "defaultSourceValue": "event"})
                )
            ])])
        ),
        metadata=MetaData(
            name='Get field type',
            desc='This plugin returns type and length (if it exists) of the given field.',
            icon='plugin',
            group=["Operations"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "field_info": PortDoc(desc="This port returns field info.")
                }
            )
        )
    )
