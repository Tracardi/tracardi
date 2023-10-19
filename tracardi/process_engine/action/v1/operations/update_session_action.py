from datetime import datetime

from tracardi.domain.session import Session
from tracardi.domain.value_object.operation import Operation
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.wrappers import lock_for_session_update


class UpdateSessionAction(ActionRunner):

    @lock_for_session_update
    async def run(self, payload: dict, in_edge=None):
        if isinstance(self.session, Session):
            if isinstance(self.session.operation, Operation):
                self.session.operation.new = True
            self.session.metadata.time.update = datetime.utcnow()
        return None


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='UpdateSessionAction',
            inputs=["payload"],
            outputs=[],
            version="0.8.2",
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
