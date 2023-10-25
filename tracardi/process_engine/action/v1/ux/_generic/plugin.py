from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from pydantic import field_validator
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    uix_source: str
    props: dict

    @field_validator("uix_source")
    @classmethod
    def validate_file_path(cls, value):
        if isinstance(value, str) and not value.endswith(".js"):
            raise ValueError("Widget file has to be .js file.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class GenericUixPlugin(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)
        props = traverser.reshape(self.config.props)
        self.ux.append({
            "tag": "div",
            "props": props
        })
        self.ux.append({
            "tag": "script",
            "props": {"src": f"{self.config.uix_source}"}
        })
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='GenericUixPlugin',
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.1',
            license="MIT + CC",
            author="Dawid Kruk",
            manual="generic_uix_action",
            init={
                "uix_source": None,
                "props": {}
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Custom widget configuration",
                        fields=[
                            FormField(
                                id="uix_source",
                                name="UIX source",
                                description="Type URL to the micro frontend source code.",
                                component=FormComponent(type="text", props={"label": "URL"})
                            ),
                            FormField(
                                id="props",
                                name="Widget props",
                                description="Type properties as key-value pairs for the widget. "
                                            "You can reference the values as dotted paths.",
                                component=FormComponent(type="keyValueList", props={"label": "Props"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Custom widget',
            desc='Shows custom ReactJS widget.',
            icon='react',
            group=["UIX Widgets"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload without any changes.")
                }
            )
        )
    )
