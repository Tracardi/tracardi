import asyncio
import re

from pydantic import BaseModel, validator

from tracardi.service.storage.driver import storage
from tracardi.service.storage.factory import StorageFor
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session


class DebugConfiguration(BaseModel):
    type: str

    @validator("type")
    def not_empty(cls, value):
        if len(value) < 1:
            raise ValueError("Event type can not be empty.")

        if value != value.strip():
            raise ValueError(f"This field must not have space. Space is at the end or start of '{value}'")

        if not re.match(
            r'^[\@a-zA-Z0-9\._\-]+$',
            value.strip()
        ):
            raise ValueError("This field must not have other characters then: letters, digits, ., _, -, @")

        return value


def validate(config: dict) -> DebugConfiguration:
    return DebugConfiguration(**config)


class DebugPayloadAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, **kwargs):
        if self.debug:
            result = await storage.driver.event.load_event_by_type(self.config.type)

            if result.total == 0:
                raise ValueError(
                    "There is no event with type `{}`. Check configuration for correct event type.".format(
                        self.config.type))

            event_data = list(result)[0]

            event = Event(**event_data)

            profile_entity = Entity(id=event.profile.id)
            session_entity = Entity(id=event.session.id)
            profile_task = asyncio.create_task(StorageFor(profile_entity).index('profile').load(Profile))
            session_task = asyncio.create_task(StorageFor(session_entity).index('session').load(Session))

            profile = await profile_task
            session = await session_task

            if session is None:
                raise ValueError(
                    "Event id `{}` has reference to empty session id `{}`. Debug stopped. This event is corrupted.".format(
                        event.id, event.session.id))

            if profile is None:
                raise ValueError(
                    "Event type `{}` has reference to empty profile id `{}`. Debug stopped. This event is corrupted.".format(
                        event.id, event.profile.id))

            self.profile.replace(profile)
            self.session.replace(session)
            self.event.replace(event)

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
                "type": "page-view",
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="type",
                            name="Event type",
                            description="Provide event type that exists in you database. Tracardi will read "
                                        "first event of provided type and will inject it into current workflow.",
                            component=FormComponent(type="text", props={"label": "Event type"})
                        )
                    ]
                ),
            ]),
            manual="debug_payload_action",
            version='0.1.1',
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
