from typing import Union

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.domain.profile import Profile
from tracardi.service.plugin.domain.config import PluginConfig


class IncrementConfig(PluginConfig):
    field: str
    increment: Union[int, float]


def validate(config: dict):
    return IncrementConfig(**config)


class IncrementAction(ActionRunner):

    config: IncrementConfig

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        dot = self._get_dot_accessor(payload if isinstance(payload, dict) else None)

        try:

            value = dot[self.config.field]

            if value is None:
                value = 0

        except KeyError:
            self.console.warning(f"Property `{self.config.field}` does not exist. Value set to 0.")
            value = 0

        if not isinstance(value, (int, float)):
            message = "Value of field '{}' is not numeric.".format(self.config.field)
            self.console.error(message)
            return Result(port="error", value={"message": message})

        value += self.config.increment

        dot[self.config.field] = value

        if self.event.metadata.profile_less is False:
            self.profile.replace(Profile(**dot.profile))

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='IncrementAction',
            inputs=["payload"],
            outputs=['payload', 'error'],
            init={"field": "profile@aux.counters", "increment": 1},
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="field",
                            name="Path to field",
                            description="Provide path to field that should be incremented. "
                                        "E.g. profile@aux.counters.boughtProducts",
                            component=FormComponent(type="dotPath", props={"label": "Field path",
                                                                           "defaultSourceValue": "profile"})
                        )
                    ]
                ),
                FormGroup(
                    fields=[
                        FormField(
                            id="increment",
                            name="Incrementation",
                            description="Provide by what number the value at provided path should "
                                        "be incremented. Default value equals 1.",
                            component=FormComponent(
                                type="text",
                                props={
                                    "label": "Incrementation"
                                })
                        )
                    ]

                ),
            ]),
            manual="increment_action",
            version='0.1',
            license="MIT + CC",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Increment counter',
            desc='Increments given field in payload, returns payload.',
            icon='plus',
            group=["Stats"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns object received by plugin in input.")
                }
            )
        )
    )
