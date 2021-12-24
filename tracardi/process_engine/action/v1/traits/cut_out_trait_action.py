from pydantic import BaseModel, validator

from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    FormFieldValidation, Documentation, PortDoc
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner


class CutOutTraitConfig(BaseModel):
    trait: str

    @validator("trait")
    def trait_should_not_be_empty(cls, value):
        if len(value) == 0:
            raise ValueError("Trait should not be empty")

        return value


def validate(config: dict):
    return CutOutTraitConfig(**config)


class CutOutTraitAction(ActionRunner):

    def __init__(self, **kwargs):
        self.property = validate(kwargs)

    async def run(self, payload: dict):

        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)
        return Result(port="trait", value=dot[self.property])


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
                            component=FormComponent(type="dotPath", props={"label": "Field path"}),
                            validation=FormFieldValidation(
                                regex=r"^[a-zA-Z0-9\@\.\-_]+$",
                                message="This field must be in Tracardi dot path format."
                            )
                        )
                    ]
                )
            ]),
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Cut out trait',
            desc='Returns defined property from payload.',
            icon='property',
            group=["Data processing"],
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
