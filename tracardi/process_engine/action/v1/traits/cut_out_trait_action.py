from typing import Optional

from pydantic import field_validator

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


class CutOutTraitConfig(PluginConfig):
    trait: str
    key: Optional[str] = None

    @field_validator("trait")
    @classmethod
    def trait_should_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Trait should not be empty")

        return value


def validate(config: dict):
    return CutOutTraitConfig(**config)


class CutOutTraitAction(ActionRunner):

    property: CutOutTraitConfig

    async def set_up(self, init):
        self.property = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)
        result = dot[self.property.trait]
        if self.property.key:
            key = self.property.key.strip()
            if key == "":
                self.console.error("Key is empty")
            return Result(port="trait", value={self.property.key.strip(): result})
        return Result(port="trait", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='CutOutTraitAction',
            inputs=['payload'],
            outputs=["trait"],
            init={
                "trait": "",
                "key": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Cut data to payload",
                    fields=[
                        FormField(
                            id="trait",
                            name="Path to data",
                            description="Provide path to field that you would like to return as output payload. "
                                        "E.g. event@session.context.browser.browser.userAgent",
                            component=FormComponent(type="dotPath", props={"label": "Field path",
                                                                           "defaultSourceValue": "event",
                                                                           "forceMode": 1})
                        ),
                        FormField(
                            id="key",
                            name="Return as",
                            description="Return the data as an object with the specified key. For example, if the "
                                        "key is \"key\" and the cut-out-value is \"value\", the returned object "
                                        "would be {\"key\": \"value\"}. If you do not want to define a key, leave "
                                        "this field empty and the data will be returned as it is.",
                            component=FormComponent(type="text", props={"label": "Key"})
                        )
                    ]
                )
            ]),
            version='0.8.0',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='cut_out_data'
        ),
        metadata=MetaData(
            name='Cut out data',
            desc='Returns a part of referenced data as payload.',
            icon='property',
            group=["Data processing"],
            purpose=['collection', 'segmentation'],
            tags=['traits', 'profile', 'memory', 'reference', 'data', 'cut'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "trait": PortDoc(desc="This port returns field selected from payload in configuration.")
                }
            )
        )
    )
