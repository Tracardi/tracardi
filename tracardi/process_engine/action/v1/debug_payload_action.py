import asyncio
import re

from pydantic import BaseModel, validator

from tracardi.service.storage.driver import storage
from tracardi.service.storage.factory import StorageFor
from tracardi_graph_runner.domain.execution_graph import ExecutionGraph
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
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

    @staticmethod
    async def _load_full_event(event_data):

        profile = None
        event = Event(**event_data)

        session_entity = Entity(id=event.session.id)
        session_task = asyncio.create_task(StorageFor(session_entity).index('session').load(Session))

        if event.metadata.profile_less is False and isinstance(event.profile, Entity):
            profile_entity = Entity(id=event.profile.id)
            profile_task = asyncio.create_task(StorageFor(profile_entity).index('profile').load(Profile))

            profile = await profile_task

        session = await session_task

        if session is None:
            raise ValueError(
                "Event id `{}` has reference to empty session id `{}`. Debug stopped. This event is corrupted.".format(
                    event.id, event.session.id))

        if event.metadata.profile_less is False and isinstance(event.profile, Entity) and profile is None:
            raise ValueError(
                "Event type `{}` has reference to empty profile id `{}`. Debug stopped. This event is corrupted.".format(
                    event.id, event.profile.id))

        return event, profile, session

    async def run(self, **kwargs):
        if self.debug:

            result = await storage.driver.event.load_event_by_type(self.config.type, limit=10)

            if result.total == 0:
                raise ValueError(
                    "There is no event with type `{}`. Check configuration for correct event type.".format(
                        self.config.type))

            for event_data in list(result):

                try:

                    event, profile, session = await self._load_full_event(event_data)

                    self.session.replace(session)
                    self.event.replace(event)
                    if event.metadata.profile_less is False:
                        if self.profile is not None and profile is not None:
                            self.profile.replace(profile)
                    else:
                        self.event.profile = None
                        self.profile = None

                        # Remove profiles in all nodes because the event is profile less
                        graph = self.execution_graph  # type: ExecutionGraph
                        if isinstance(graph, ExecutionGraph):
                            graph.remove_profiles()

                    return Result(port="event", value=self.event.dict())

                except ValueError as e:
                    self.console.warning(str(e))

            raise ValueError("There is no event with type `{}` that is consistent. See log error for details.".format(
                        self.config.type))

        else:
            # No debug mode
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
            icon='debug',
            group=["Input/Output"],
            documentation=Documentation(
                outputs={
                    "event": PortDoc(desc="This port returns first event with type defined in configuration.")
                },
                inputs={}
            )
        )
    )
