from asyncio import sleep

from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormComponent, \
    FormFieldValidation, FormField
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class SleepAction(ActionRunner):

    def __init__(self, **kwargs):
        self.wait = kwargs['wait'] if 'wait' in kwargs else 0

    async def run(self, payload):
        await sleep(float(self.wait))
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
            init={"sleep": 1},
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="sleep",
                            name="Wait",
                            description="Provide number of seconds to wait before next action.",
                            component=FormComponent(
                                type="text",
                                props={
                                    "label": "Number of seconds"
                                }),
                            validation=FormFieldValidation(
                                regex=r"^\d+$",
                                message="This field must be numeric."
                            )
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
            group=["Time"]
        )
    )
