import json

from tracardi.service.notation.dict_traverser import DictTraverser
from .configuration import Config
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


def validate(config: dict) -> Config:
    return Config(**config)


class GenericJsScriptPlugin(ActionRunner):
    config: Config

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        attributes = json.loads(self.config.attributes)

        if not isinstance(attributes, dict):
            raise ValueError(f"Script attributes must be a dictionary, {type(attributes)} given.")

        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)
        attributes = traverser.reshape(attributes)

        self.ux.append({
            "tag": "script",
            "props": attributes,
            "content": self.config.content
        })

        return Result(port="response", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=GenericJsScriptPlugin.__name__,
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.4',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "attributes": "{}",
                "content": ""
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Custom JavaScript tag configuration",
                        fields=[
                            FormField(
                                id="attributes",
                                name="Script attributes",
                                description="Type attributes as key-value pairs for the script tag. "
                                            "If the tag has source type it here as \"src\": <source>.",
                                component=FormComponent(type="json", props={"label": "Attributes"})
                            ),
                            FormField(
                                id="content",
                                name="Script content",
                                description="Type script content body. It should be a javascript code.",
                                component=FormComponent(type="text", props={"label": "Javascript"})
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Javascript tag',
            desc='Injects custom Javascript tag.',
            icon='javascript',
            group=["UIX Widgets"]
        )
    )
