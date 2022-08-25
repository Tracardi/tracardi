from tracardi.domain.session import Session
from tracardi.domain.value_object.operation import Operation
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner


class UpdateSessionAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None):
        if self.debug is True:
            self.console.warning("Session may not be updated in debug mode.")
        elif isinstance(self.session, Session) and isinstance(self.session.operation, Operation):
            self.session.operation.new = True
        return None


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='UpdateSessionAction',
            inputs=["payload"],
            outputs=[],
            version="0.6.2",
            init=None,
            manual="update_session_action"
        ),
        metadata=MetaData(
            name='Update session',
            desc='Updates session in storage.',
            icon='store',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload object.")
                },
                outputs={}
            )
        )
    )
