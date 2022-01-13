from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.action_runner import ActionRunner
from pydantic import BaseModel, validator
from typing import Dict, Any
from tracardi.service.plugin.domain.result import Result


class Config(BaseModel):
    condition_value: str
    switch: Dict[str, Any]

    @validator('switch')
    def validate_switch(cls, value):
        if not value:
            raise ValueError("Switch cannot be empty.")
        return value


def validate(config: dict):
    return Config(**config)


class SwitchAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        self.config.condition_value = dot[self.config.condition_value]

        self.config.switch = {dot[key]: dot[value] for key, value in self.config.switch.items()}

        value = self.config.switch.get(self.config.condition_value, None)

        return Result(port="result", value={"value": value})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SwitchAction',
            inputs=["payload"],
            outputs=["result"],
            version='0.6.1',
            license="MIT",
            author="Dawid Kruk",
            manual="switch_action",
            init={
                "condition_value": None,
                "switch": {}
            },
            form=Form(
                name="Plugin configuration",
                groups=[
                    FormGroup(
                        fields=[
                            FormField(
                                id="condition_value",
                                name="Condition value",
                                description="Please provide a path to the condition value.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="switch",
                                name="Switch",
                                description="Please provide key-value pairs. Value will be returned if condition value "
                                            "is the same as key.",
                                component=FormComponent(type="keyValueList", props={"label": "List"})
                            )
                        ]
                    )
                ]
            )

        ),
        metadata=MetaData(
            name='Switch',
            desc='Returns one of given values in terms of given condition value.',
            type='flowNode',
            icon='plugin',
            group=["Conditions"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This ports returns result value, according to configuration.")
                }
            )
        )
    )
