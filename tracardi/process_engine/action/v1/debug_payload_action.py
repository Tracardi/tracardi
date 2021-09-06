import asyncio
from tracardi.service.storage.factory import StorageFor
from tracardi.service.storage.helpers.event_loader import load_event_by_type
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session


class DebugPayloadAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'event' not in kwargs or 'type' not in kwargs['event']:
            raise ValueError("Please define event.type in config section.")
        self.event_type = kwargs['event']['type']

    async def run(self, **kwargs):
        if self.debug:
            result = await load_event_by_type(self.event_type)

            if result.total == 0:
                raise ValueError(
                    "There is no event with type `{}`. Check configuration for correct event type.".format(
                        self.event_type))

            event_data = list(result)[0]

            self.event = Event(**event_data)

            profile_entity = Entity(id=self.event.profile.id)
            session_entity = Entity(id=self.event.session.id)
            profile_task = asyncio.create_task(StorageFor(profile_entity).index('profile').load(Profile))
            session_task = asyncio.create_task(StorageFor(session_entity).index('session').load(Session))

            profile = await profile_task
            session = await session_task

            if session is None:
                raise ValueError(
                    "Event id `{}` has reference to empty session id `{}`. Debug stopped. This event is corrupted.".format(
                        self.event.id, self.event.session.id))

            self.session.replace(session)

            if profile is None:
                raise ValueError(
                    "Event type `{}` has reference to empty profile id `{}`. Debug stopped. This event is corrupted.".format(
                        self.event.id, self.event.profile.id))

            self.profile.replace(profile)

            return Result(port="event", value=self.event.dict())

        return Result(port="event", value=self.event.dict())


def register() -> Plugin:
    return Plugin(
        start=True,
        debug=True,
        spec=Spec(
            module='tracardi.process_engine.action.v1.debug_payload_action',
            className='DebugPayloadAction',
            inputs=[],
            outputs=["event"],
            init={
                "event": {
                    "type": None,
                }
            },
            manual="debug_payload_action",
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Debug',
            desc='Loads debug payload into flow. This action is executed only in debug mode. ' +
                 'Use it to inject payload defined it config to analyse you workflow.',
            keywords=['start node'],
            type='flowNode',
            width=100,
            height=100,
            icon='debug',
            group=["Input/Output"]
        )
    )
