from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi_plugin_sdk.action_runner import ActionRunner


class UpdateEventAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, payload):
        self.event.update = True
        return None


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.operations.update_event_action',
            className='UpdateEventAction',
            inputs=["payload"],
            outputs=[],
            version="0.6.0.1",
            init=None,
            manual="update_profile_action"
        ),
        metadata=MetaData(
            name='Update event',
            desc='Updates event in storage.',
            icon='event',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={}
            )
        )
    )
