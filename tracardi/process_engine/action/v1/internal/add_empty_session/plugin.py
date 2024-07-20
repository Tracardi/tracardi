from uuid import uuid4
from tracardi.domain.entity import PrimaryEntity
from tracardi.domain.event import EventSession
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.value_object.operation import Operation
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.elastic.interface.collector.mutation.session import save_session_to_db


class AddEmptySessionAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None) -> Result:

        session = Session(
                id=str(uuid4()),
                profile=PrimaryEntity(id=self.profile.id) if self.profile is not None else None,
                metadata=SessionMetadata(),
                operation=Operation(update=True)
            )
        self.session = session
        self.event.session = EventSession(
                id=session.id,
                start=session.metadata.time.insert,
                duration=session.metadata.time.duration
            )

        self.execution_graph.set_sessions(session)
        await save_session_to_db(session)

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
