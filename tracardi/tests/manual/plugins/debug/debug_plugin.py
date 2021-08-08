from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner


class DebugPlugin(ActionRunner):

    def __init__(self):
        pass

    async def run(self, payload):
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        spec=Spec(
            module='task_plugins.debug.debug_plugin',
            className='DebugPlugin',
            inputs=[],
            outputs=["payload"]
        ),
        metadata=MetaData(
            name='Debug',
            desc='Logs payload for debugging purposes.',
            type='flowNode',
            width=100,
            height=100,
            icon='debug'
        )
    )
