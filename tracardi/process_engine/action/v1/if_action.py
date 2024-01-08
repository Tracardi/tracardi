from typing import Optional

from pydantic import field_validator
from tracardi.service.plugin.domain.config import PluginConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner

from tracardi.process_engine.tql.condition import Condition
from tracardi.service.utils.getters import get_entity_id
from tracardi.service.value_threshold_manager import ValueThresholdManager


class IfConfiguration(PluginConfig):
    condition: str
    trigger_once: bool = False
    pass_payload: bool = True
    ttl: int = 0

    @field_validator("condition")
    @classmethod
    def is_valid_condition(cls, value):
        try:
            _condition = Condition()
            _condition.parse(value)
        except Exception as e:
            raise ValueError(str(e))

        return value

    @field_validator("ttl")
    @classmethod
    def is_bigger_then_zero(cls, value):
        if value < 0:
            raise ValueError("This value must be greater then 0")

        return value


def validate(config: dict) -> IfConfiguration:
    return IfConfiguration(**config)


class IfAction(ActionRunner):

    config: IfConfiguration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Optional[Result]:

        if self.config.condition is None:
            raise ValueError("Condition is not set. Define it in config section.")

        dot = self._get_dot_accessor(payload)

        condition = Condition()
        result = await condition.evaluate(self.config.condition, dot)

        if self.config.trigger_once:
            vtm = ValueThresholdManager(
                name=self.node.name,
                node_id=self.node.id,
                profile_id=get_entity_id(self.profile),
                ttl=int(self.config.ttl),
                debug=self.debug
            )

            allow_passage = await vtm.pass_threshold(result)

            if not allow_passage:
                return None

        if result:
            return Result(port="true", value=payload if self.config.pass_payload else {"result": True})
        else:
            return Result(port="false", value=payload if self.config.pass_payload else {"result": False})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.if_action',
            className='IfAction',
            inputs=["payload"],
            outputs=["true", "false"],
            init={
                "condition": "",
                "trigger_once": False,
                "pass_payload": True,
                "ttl": 0
            },
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
                        ),
                        FormField(
                            id="trigger_once",
                            name="Return value only once per condition change",
                            description="It will trigger the relevant port only once per condition change. Otherwise "
                                        "the flow will be stopped.",
                            component=FormComponent(type="bool", props={"label": "Trigger once per condition change"})
                        ),
                        FormField(
                            id="ttl",
                            name="Expire trigger again after",
                            description="If the value is set to 0, the event will only occur once and will not be "
                                        "triggered again unless the conditions change. However, if a value greater "
                                        "than 0 is set, the event will be triggered again after the specified "
                                        "number of seconds, regardless of whether the conditions have changed or not.",
                            component=FormComponent(type="text", props={"label": "Suppression time to live"})
                        ),
                        FormField(
                            id="pass_payload",
                            name="Return input payload instead of True/False",
                            description="It will return input payload on the output ports if enabled "
                                        "otherwise True/False.",
                            component=FormComponent(type="bool", props={"label": "Return input payload"})
                        )
                    ]
                ),
            ]),
            manual="if_action",
            version='0.7.4',
            license="MIT + CC",
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
