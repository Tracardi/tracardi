from uuid import uuid4
from tracardi.domain.entity import Entity
from tracardi.domain.event import EventSession
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.value_object.operation import Operation
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage


class AddEmptySessionAction(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, payload: dict, in_edge=None) -> Result:

        if self.debug is True:
            self.console.warning(
                "Your requested an update of the event session but events may not be updated in debug mode.")

        session = Session(
                id=str(uuid4()),
                profile=Entity(id=self.profile.id) if self.profile is not None else None,
                metadata=SessionMetadata(),
                operation=Operation(
                    update=True if self.debug is False else False
                )
            )
        self.session = session
        self.event.session = EventSession(
                id=session.id,
                start=session.metadata.time.insert,
                duration=session.metadata.time.duration
            )
        self.event.update = True
        self.execution_graph.set_sessions(session)
        await storage.driver.session.save(session)

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
            license="MIT",
            author="Risto Kowaczewski",
            init={},
            form=None,

        ),
        metadata=MetaData(
            name='Add empty session',
            desc='Ads new session to the event. Empty session gets created with random id.',
            icon='session',
            group=["Operations"],
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
