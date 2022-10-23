from pydantic import validator
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner

from tracardi.process_engine.tql.condition import Condition


class IfConfiguration(PluginConfig):
    condition: str

    @validator("condition")
    def is_valid_condition(cls, value):
        try:
            _condition = Condition()
            _condition.parse(value)
        except Exception as e:
            raise ValueError(str(e))

        return value


def validate(config: dict) -> IfConfiguration:
    return IfConfiguration(**config)


class IfAction(ActionRunner):

    config: IfConfiguration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        if self.config.condition is None:
            raise ValueError("Condition is not set. Define it in config section.")

        dot = self._get_dot_accessor(payload)

        condition = Condition()
        if await condition.evaluate(self.config.condition, dot):
            return Result(port="true", value=payload)
        else:
            return Result(port="false", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.if_action',
            className='IfAction',
            inputs=["payload"],
            outputs=["true", "false"],
            init={"condition": ""},
            form=Form(groups=[
                FormGroup(
                    name="Condition statement",
                    fields=[
                        FormField(
                            id="condition",
                            name="If condition statement",
                            description="Provide condition for IF statement. If the condition is met then the payload "
                                        "will be returned on TRUE port if not then FALSE port is triggered.",
                            component=FormComponent(type="textarea", props={"label": "condition"})
                        )
                    ]
                ),
            ]),
            manual="if_action",
            version='0.7.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='If',
            desc='This a conditional action that conditionally runs a branch of workflow.',
            tags=['condition'],
            purpose=['collection', 'segmentation'],
            type="condNode",
            icon='if',
            group=['Flow control'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "true": PortDoc(desc="Returns payload if the defined condition is met."),
                    "false": PortDoc(desc="Returns payload if the defined condition is NOT met.")
                }
            )
        )
    )
