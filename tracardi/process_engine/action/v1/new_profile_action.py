from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class NewProfileAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, payload):
        if self.profile.operation.new:
            return Result(port="TRUE", value=payload)

        return Result(port="FALSE", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.new_profile_action',
            className='NewProfileAction',
            inputs=["payload"],
            outputs=['TRUE', 'FALSE'],
            init=None,
            manual="new_profile_action",
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Is it a new profile',
            desc='If new profile then it returns true on TRUE output, otherwise returns false on FALSE port.',
            keywords=['condition'],
            type='flowNode',
            width=200,
            height=100,
            icon='question',
            group=["Conditions"]
        )
    )
