from asyncio import sleep

from pydantic import BaseModel, validator
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormComponent, FormField, \
    Documentation, PortDoc
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class SleepConfiguration(BaseModel):
    wait: float

    @validator('wait')
    def is_bigger_then_zero(cls, value):
        if value < 0:
            raise ValueError("I can not wait less then zero seconds.")
        return value


def validate(config: dict) -> SleepConfiguration:
    return SleepConfiguration(**config)


class SleepAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):
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
            license="MIT",
            author="Risto Kowaczewski",
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
            name='Wait',
            desc='Waits workflow for given time.',
            type='flowNode',
            width=100,
            height=100,
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
