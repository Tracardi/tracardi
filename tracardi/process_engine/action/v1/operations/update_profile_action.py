from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner


class UpdateProfileAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, void):
        self.profile.operation.update = True
        return None


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.operations.update_profile_action',
            className='UpdateProfileAction',
            inputs=["void"],
            outputs=[],
            init=None,
            manual="update_profile_action"
        ),
        metadata=MetaData(
            name='Update profile',
            desc='Updates profile in storage.',
            type='flowNode',
            width=200,
            height=100,
            icon='store',
            group=["Operations"]
        )
    )
