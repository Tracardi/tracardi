from tracardi.service.utils.date import now_in_utc

from tracardi.domain.session import Session
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner


class UpdateSessionAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None):
        if isinstance(self.session, Session):
            self.session.set_updated_in_workflow()
            self.session.metadata.time.update = now_in_utc()
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
