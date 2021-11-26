from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class NewProfileAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, payload):
        if self.profile.operation.new:
            return Result(port="true", value=payload)

        return Result(port="false", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.new_profile_action',
            className='NewProfileAction',
            inputs=["payload"],
            outputs=['true', 'false'],
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
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                },
                outputs={
                    "true": PortDoc(desc="This port returns payload if the defined condition is met."),
                    "false": PortDoc(desc="This port returns payload if the defined condition is NOT met.")
                }
            ),
            width=200,
            height=100,
            icon='question',
            group=["Conditions"]
        )
    )
