from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner


class UpdateEventAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None):
        self.event.update = True
        if self.debug is True:
            self.console.warning("Events may not be updated in debug mode.")
        return None


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='UpdateEventAction',
            inputs=["payload"],
            outputs=[],
            version="0.6.0.1",
            init=None,
            manual="update_event_action"
        ),
        metadata=MetaData(
            name='Update event',
            desc='Updates event in storage.',
            icon='event',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload object.")
                },
                outputs={}
            )
        )
    )
