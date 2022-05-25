from datetime import datetime
from uuid import uuid4

import asyncio

from tracardi.domain.entity import Entity
from tracardi.domain.event import EventSession
from tracardi.domain.metadata import ProfileMetadata
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.time import ProfileTime, ProfileVisit
from tracardi.domain.value_object.operation import Operation
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage


class AddEmptyProfileAction(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, payload):

        now = datetime.utcnow()
        profile = Profile(
            id=str(uuid4()),
            metadata=ProfileMetadata(
                time=ProfileTime(
                    insert=now,
                    visit=ProfileVisit(
                        count=1,
                        current=datetime.utcnow()
                    )
                )
            ),
            operation=Operation(update=True)
        )

        self.event.profile = profile
        self.event.metadata.profile_less = False
        if self.debug is True:
            self.console.warning(
                "Your requested an update of event profile but events may not be updated in debug mode.")
        else:
            self.event.update = True
        self.execution_graph.set_profiles(profile)

        coroutines = [storage.driver.profile.save_profile(profile)]

        session = Session(
            id=str(uuid4()),
            profile=Entity(id=profile.id),
            metadata=SessionMetadata(),
            operation=Operation(update=True)
        )

        if self.session is not None:
            self.console.warning(f"Old session {self.session.id} was replaced by new session {session.id}. "
                                 f"Replacing session is not a good practice if you already have a session.")

        self.session = session

        self.event.session = EventSession(
            id=session.id,
            start=session.metadata.time.insert,
            duration=session.metadata.time.duration
        )
        self.execution_graph.set_sessions(session)

        if not self.tracker_payload.is_on('saveSession', default=True):
            coroutines.append(storage.driver.session.save(session))

        await asyncio.gather(*coroutines)

        return Result(port='payload', value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='AddEmptyProfileAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.7.0',
            license="MIT",
            author="Risto Kowaczewski",
            init={},
            form=None,

        ),
        metadata=MetaData(
            name='Add empty profile',
            desc='Ads new profile to the event. Empty profile gets created with random id.',
            icon='profile',
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
