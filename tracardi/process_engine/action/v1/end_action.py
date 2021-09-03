from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner


class EndAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, payload):
        return None


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.end_action',
            className='EndAction',
            inputs=["payload"],
            outputs=[],
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"

        ),
        metadata=MetaData(
            name='End',
            desc='Ends workflow.',
            type='flowNode',
            width=100,
            height=100,
            icon='stop',
            group=["Input/Output"]
        )
    )
