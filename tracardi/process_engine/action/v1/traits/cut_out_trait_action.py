from pydantic import validator

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.config import PluginConfig


class CutOutTraitConfig(PluginConfig):
    trait: str

    @validator("trait")
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
        return Result(port="trait", value=dot[self.property.trait])


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.traits.cut_out_trait_action',
            className='CutOutTraitAction',
            inputs=['payload'],
            outputs=["trait"],
            init={
                "trait": ""
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
                        )
                    ]
                )
            ]),
            version='0.6.1',
            license="MIT",
            author="Risto Kowaczewski"
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
