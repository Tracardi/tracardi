from asyncio import sleep

from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class SleepAction(ActionRunner):

    def __init__(self, **kwargs):
        self.sleep = kwargs['sleep'] if 'sleep' in kwargs else 0

    async def run(self, payload):
        await sleep(self.sleep)
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.sleep_action',
            className='SleepAction',
            inputs=["payload"],
            outputs=["payload"],
            version='0.1.1',
            license="MIT",
            author="Risto Kowaczewski",
            init={"sleep": 1}

        ),
        metadata=MetaData(
            name='Sleep',
            desc='Sleeps workflow.',
            type='flowNode',
            width=100,
            height=100,
            icon='sleep',
            group=["Time"]
        )
    )
