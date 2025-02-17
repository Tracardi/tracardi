from uuid import uuid4
from tracardi.domain.event_session import EventSession
from tracardi.domain.flat_session import FlatSession
from tracardi.domain.session import SessionMetadata

from tracardi.service.dependency.adapters.big_data_adapter import *
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class AddEmptySessionAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None) -> Result:

        session = FlatSession.new(id=str(uuid4()), profile_id=self.profile.id if self.profile is not None else None) << [
            ('metadata', SessionMetadata().model_dump())
        ]
        self.session = session
        self.event.session = EventSession(
                id=session.id,
                start=session['metadata.time.insert'],
                duration=session['metadata.time.duration']
            )

        self.execution_graph.set_sessions(session)
        await bd_session_adapter.save_session_to_db(session)

        self.set_tracker_option("saveSession", True)

        return Result(port='payload', value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='AddEmptySessionAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.7.0',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="internal/add_empty_session",
            init=None,
            form=None
        ),
        metadata=MetaData(
            name='Create empty session',
            desc='Ads new session to the event. Empty session gets created with random id.',
            icon='session',
            group=["Operations"],
            keywords=['new', 'add', 'create'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns input payload.")
                }
            )
        )
    )
