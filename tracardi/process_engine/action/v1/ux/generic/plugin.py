from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from pydantic import validator
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.config import PluginConfig


class Config(PluginConfig):
    uix_source: str
    path: str
    props: dict

    @validator("path")
    def validate_file_path(cls, value):
        if isinstance(value, str) and not value.endswith(".js"):
            raise ValueError("Widget file has to be .js file.")
        return value


def validate(config: dict) -> Config:
    return Config(**config)


class GenericUixPlugin(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

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
            "props": {"src": f"{self.config.uix_source}{self.config.path}"}
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
            license="MIT",
            author="Dawid Kruk",
            manual="generic_uix_action",
            init={
                "uix_source": None,
                "path": None,
                "props": {}
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="uix_source",
                                name="UIX source",
                                description="Type URL to the micro frontend source code.",
                                component=FormComponent(type="text", props={"label": "URL"})
                            ),
                            FormField(
                                id="path",
                                name="File path",
                                description="Type the path to the file in selected UIX source, e.g. /files/widget.js",
                                component=FormComponent(type="text", props={"label": "Path"})
                            ),
                            FormField(
                                id="props",
                                name="Widget props",
                                description="Type properties as key-value pairs for the widget. "
                                            "You can reference the values as  dotted paths.",
                                component=FormComponent(type="keyValueList", props={"label": "Props"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Show custom widget',
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
