from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class ReadSessionAction(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, payload):
        return Result(port="payload", value=self.session.dict())


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.read_session_action',
            className='ReadSessionAction',
            inputs=["payload"],
            outputs=['payload'],
            init=None,
            manual="read_session_action",
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Read session',
            desc='Loads session data and returns it.',
            type='flowNode',
            width=200,
            height=100,
            icon='json',
            group=["Read"]
        )
    )
