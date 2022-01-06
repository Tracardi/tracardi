import asyncio
import json
import re
from datetime import datetime
from json import JSONDecodeError
from typing import Tuple, Optional

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
    type: str = ""
    profile_less: bool = False
    session_less: bool = False
    properties: str = ""

    @validator("properties")
    def convert_to_json_id_dict(cls, value):
        if isinstance(value, dict):
            value = json.dumps(value)
        return value

    @validator("type")
    def not_empty(cls, value):
        if len(value) != 0:

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

    async def _create_full_event(self, event_data) -> Tuple[Event, Optional[Profile], Optional[Session]]:

        session = None
        profile = None
        event = Event(**event_data)
        event.metadata.profile_less = self.config.profile_less

        if self.config.properties != "":
            try:
                event.properties = json.loads(self.config.properties)
            except JSONDecodeError as e:
                self.console.warning(str(e))

        if event.session is not None:
            session_entity = Entity(id=event.session.id)
            session = await StorageFor(session_entity).index('session').load(Session)

        if self.config.profile_less is False and isinstance(event.profile, Entity):
            profile_entity = Entity(id=event.profile.id)
            profile = await StorageFor(profile_entity).index('profile').load(Profile)

        if self.config.profile_less is False and isinstance(event.profile, Entity) and profile is None:
            raise ValueError(
                "Event type `{}` has reference to empty profile id `{}`. Debug stopped. This event is corrupted.".format(
                    event.id, event.profile.id))

        return event, profile, session

    async def run(self, **kwargs):
        if self.debug:

            if self.config.type is None or self.config.type == "":

                events = [
                    {
                        "id": "@debug-event-id",
                        "metadata": {
                            "time": {
                                "insert": datetime.utcnow()
                            },
                            "ip": "127.0.0.1",
                            "profile_less": False
                        },
                        "source": {
                            "id": "debug-source"
                        },
                        "type": "debug-event-type",
                        "properties": "{}",
                        "context": {
                            "config": {},
                            "params": {}
                        }
                    }
                ]

            else:
                result = await storage.driver.event.load_event_by_type(self.config.type, limit=10)

                if result.total == 0:
                    raise ValueError(
                        "There is no event with type `{}`. Check configuration for correct event type.".format(
                            self.config.type))

                events = list(result)

            for event_data in events:

                try:

                    event, profile, session = await self._create_full_event(event_data)

                    self.event.replace(event)
                    self.event.session = session
                    self.event.source = event.source

                    # Session can be None is user requested not to save it.
                    if self.config.session_less is True or session is None:
                        self.event.session = None
                        self.session = None

                        # Remove session in all nodes because the event is session less
                        graph = self.execution_graph  # type: ExecutionGraph
                        if isinstance(graph, ExecutionGraph):
                            graph.set_sessions(None)

                    elif self.session is not None:
                        self.session.replace(session)

                    # Event can be profile less if collected via webhook
                    if self.config.profile_less is True:
                        self.event.profile = None
                        self.profile = None

                        # Remove profiles in all nodes because the event is profile less
                        graph = self.execution_graph  # type: ExecutionGraph
                        if isinstance(graph, ExecutionGraph):
                            graph.set_profiles(None)
                    else:
                        if self.profile is not None and profile is not None:
                            self.profile.replace(profile)

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
                "profile_less": False,
                "session_less": False,
                "properties": ""
            },
            form=Form(groups=[
                FormGroup(
                    name="Load existing event type",
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
                FormGroup(
                    name="Modify event",
                    fields=[
                        FormField(
                            id="profile_less",
                            name="Profileless event",
                            description="Profileless events are events that does not attach profile data.",
                            component=FormComponent(type="bool", props={"label": "Profileless event"})
                        ),
                        FormField(
                            id="session_less",
                            name="Sessionless event",
                            description="Sessionless events may occur when user did not want session to be saved.",
                            component=FormComponent(type="bool", props={"label": "Sessionless event"})
                        ),
                        FormField(
                            id="properties",
                            name="Payload properties",
                            description="Set payload properties. If this field is not empty it will override the "
                                        "loaded event properties.",
                            component=FormComponent(type="json", props={"label": "Payload properties"})
                        )
                    ]
                ),
            ]),
            manual="debug_payload_action",
            version='0.6.0.1',
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
