from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class NewProfileAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, void):
        if self.profile.operation.new:
            return Result(port="TRUE", value=True)

        return Result(port="FALSE", value=False)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='app.process_engine.action.v1.new_profile_action',
            className='NewProfileAction',
            inputs=["void"],
            outputs=['TRUE', 'FALSE'],
            init=None,
            manual="new_profile_action"
        ),
        metadata=MetaData(
            name='New profile',
            desc='If new profile then it returns true on TRUE output, otherwise returns false on FALSE port.',
            type='flowNode',
            width=200,
            height=100,
            icon='question',
            group=["Processing"]
        )
    )
