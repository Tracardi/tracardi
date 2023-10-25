from asyncio import sleep

from pydantic import field_validator
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormComponent, FormField, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.domain.config import PluginConfig


class SleepConfiguration(PluginConfig):
    wait: float

    @field_validator('wait')
    @classmethod
    def is_bigger_then_zero(cls, value):
        if value < 0:
            raise ValueError("Wait value has to be greater than or equal to 0.")
        return value


def validate(config: dict) -> SleepConfiguration:
    return SleepConfiguration(**config)


class SleepAction(ActionRunner):

    config: SleepConfiguration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        await sleep(float(self.config.wait))
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.time.sleep_action',
            className='SleepAction',
            inputs=["payload"],
            outputs=["payload"],
            version='0.1.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='sleep',
            init={"wait": 1},
            form=Form(groups=[
                FormGroup(
                    name="Delay workflow",
                    fields=[
                        FormField(
                            id="wait",
                            name="Wait",
                            description="Provide number of seconds to wait before next action. This value can also "
                                        "be a fraction of a second.",
                            component=FormComponent(
                                type="text",
                                props={
                                    "label": "Number of seconds"
                                })
                        )
                    ]
                ),
            ]),

        ),
        metadata=MetaData(
            name='Sleep',
            desc='Stops workflow for given time.',
            icon='sleep',
            group=["Time"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns exactly same payload as given one.")
                }
            )
        )
    )
