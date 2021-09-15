from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner


class JoinAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, payload):
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.join_action',
            className='JoinAction',
            inputs=["payload"],
            outputs=["payload"],
            init=None,
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Join',
            desc='This action waits for previous actions to finish working. It passes payload '
                 'it recevied without any modifications.',
            type='flowNode',
            width=100,
            height=100,
            icon='join',
            group=["Flow"]
        )
    )
