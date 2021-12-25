from typing import Union

from pydantic import BaseModel, validator
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from tracardi.domain.profile import Profile


class DecrementConfig(BaseModel):
    field: str
    decrement: Union[float, int]

    @validator('field')
    def field_must_match(cls, value, values, **kwargs):
        if not value.startswith('profile@stats.counters'):
            raise ValueError(f"Only fields inside `profile@stats.counters` can be decremented. Field `{value}` given.")
        return value


def validate(config: dict):
    return DecrementConfig(**config)


class DecrementAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):

        dot = self._get_dot_accessor(payload)

        try:

            value = dot[self.config.field]

            if value is None:
                value = 0

        except KeyError:
            value = 0

        if type(value) != int:
            raise ValueError("Value of field '{}' is not numeric.".format(self.config.field))

        value -= self.config.decrement

        dot[self.config.field] = value

        if self.event.metadata.profile_less is False:
            self.profile.replace(Profile(**dot.profile))

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.decrement_action',
            className='DecrementAction',
            inputs=["payload"],
            outputs=['payload'],
            init={"field": "", "decrement": 1},
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="field",
                            name="Path to field",
                            description="Provide path to field that should be decremented. "
                                        "E.g. profile@stats.counters.boughtProducts",
                            component=FormComponent(type="dotPath", props={"label": "Field path"})
                        )
                    ]
                ),
                FormGroup(
                    fields=[
                        FormField(
                            id="decrement",
                            name="Decrementation",
                            description="Provide by what number the value at provided path should be "
                                        "decremented. Default value equals 1.",
                            component=FormComponent(
                                type="text",
                                props={
                                    "label": "Decrementation"
                                })
                        )
                    ]
                ),
            ]),
            manual="decrement_action",
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Decrement counter',
            desc='Decrement profile stats.counters value. Returns payload',
            icon='minus',
            group=["Stats"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns taken object with field from configuration decremented "
                                            "by value from configuration.")
                }
            )
        )
    )
