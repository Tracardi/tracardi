from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class ReadProfileAction(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, void):
        return Result(port="profile", value=self.profile.dict())


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='app.process_engine.action.v1.read_profile_action',
            className='ReadProfileAction',
            inputs=["void"],
            outputs=['profile'],
            init={},
            manual="read_profile_action"
        ),
        metadata=MetaData(
            name='Read profile',
            desc='Loads profile data and returns it.',
            type='flowNode',
            width=200,
            height=100,
            icon='profile',
            group=["Read"]
        )
    )
