from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class Config(PluginConfig):
    field: str
    find: str
    replace: str


def validate(config: dict) -> Config:
    return Config(**config)


class StringReplaceAction(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        dot = self._get_dot_accessor(payload)
        value = dot[self.config.field]

        if not isinstance(value, str):
            raise ValueError(f"Field '{self.config.field}' is not a string.")

        # Perform string replacement
        new_value = value.replace(self.config.find, self.config.replace)

        dot[self.config.field] = new_value

        return Result(port="output", value=payload)

def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='StringReplaceAction',
            inputs=["payload"],
            outputs=["output"],
            version='1.0.0',
            license="MIT",
            author="Akhil Bisht",
            init={
                "field": None,
                "find": None,
                "replace": None
            },
            manual="string_replace_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="String Replacement Plugin Configuration",
                        fields=[
                            FormField(
                                id="field",
                                name="Field",
                                description="The field to perform string replacement on.",
                                component=FormComponent(
                                    type="text",
                                    props={
                                        "label": "Field"
                                    }
                                )
                            ),
                            FormField(
                                id="find",
                                name="Find",
                                description="The substring to find in the field.",
                                component=FormComponent(
                                    type="text",
                                    props={
                                        "label": "Find"
                                    }
                                )
                            ),
                            FormField(
                                id="replace",
                                name="Replace",
                                description="The replacement string.",
                                component=FormComponent(
                                    type="text",
                                    props={
                                        "label": "Replace"
                                    }
                                )
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='String Replace',
            desc='Replace a specified string within a field in the payload.',
            icon='replace',
            group=["String"],
            tags=['string', 'replace'],
            purpose=['modification'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={"output": PortDoc(desc="This port returns the modified payload with the string replacement.")}
            )
        )
    )

