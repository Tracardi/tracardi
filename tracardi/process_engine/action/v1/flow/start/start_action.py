import json
from json import JSONDecodeError
from uuid import uuid4

from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session, SessionMetadata
from tracardi.domain.time import EventTime
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from .model.configuration import Configuration
from tracardi.service.wf.domain.graph_invoker import GraphInvoker
from typing import Optional
from tracardi.domain.event import Event, EventSession
from tracardi.domain.entity import Entity


def validate(config: dict):
    return Configuration(**config)


class StartAction(ActionRunner):
    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def debug_run(self):

        # Set debug event

        session = Session(id=self.config.session_id if self.config.session_id else str(uuid4()),
                          metadata=SessionMetadata())
        profile = Profile(id=self.config.profile_id if self.config.profile_id else str(uuid4()))

        event_session = EventSession(id=session.id)
        event_profile = Entity(id=profile.id)

        source = Entity(id="@debug-event-source")

        event_type = self.config.event_type.id if self.config.event_type.id else "@debug-event-type"

        event_id = self.config.event_id if self.config.event_id else str(uuid4())

        try:
            properties = json.loads(self.config.properties)
        except JSONDecodeError:
            self.console.error("Could not decode properties as JSON in start node.")
            properties = {}

        event = Event(
            metadata=EventMetadata(time=EventTime(), debug=True),
            id=event_id,
            type=event_type,
            source=source,
            profile=event_profile,
            session=event_session,
            properties=properties,
            context={
                "config": {
                    "debugger": True
                },
                "params": {}
            }
        )

        if profile:
            _profile = await storage.driver.profile.load_by_id(profile.id)
            if _profile:
                profile = _profile.to_entity(Profile)

        if session:
            _session = await storage.driver.session.load_by_id(session.id)
            if _session:
                session = _session

        try:

            self.event.replace(event)
            self.event.session = session
            self.event.source = source
            self.event.profile = profile

            # Remove session in all nodes because the event is session less
            graph = self.execution_graph  # type: GraphInvoker
            if isinstance(graph, GraphInvoker):
                graph.set_sessions(session)

            # Remove profiles in all nodes because the event is profile less
            graph = self.execution_graph  # type: GraphInvoker
            if isinstance(graph, GraphInvoker):
                graph.set_profiles(profile)

            return Result(port="payload", value={})

        except ValueError as e:
            self.console.warning(str(e))

    async def production_run(self):
        self.event.metadata.debug = self.config.debug

        allowed_event_types = self.config.get_allowed_event_types()

        if len(allowed_event_types) > 0 and self.event.type not in self.config.get_allowed_event_types():
            return None

        return Result(port="payload", value={})

    async def run(self, *args, **kwargs) -> Optional[Result]:
        if self.debug is True:
            return await self.debug_run()
        else:
            return await self.production_run()


def register() -> Plugin:
    return Plugin(
        start=True,
        debug=False,
        spec=Spec(
            module=__name__,
            className='StartAction',
            inputs=[],
            outputs=["payload"],
            init={
                "debug": False,
                "event_types": [],
                "properties": "{}",
                "event_id": None,
                "profile_id": None,
                "session_id": None,
                "event_type": {
                    "name": "",
                    "id": ""
                },
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="event_types",
                            name="Accept only the following event types",
                            description="This node will start the workflow only if the defined below event-types are consumed. "
                                        "If left empty the node will trigger regardless of the event-type and all the events "
                                        "will be accepted. To add none-existing event-type, type its name and press ENTER.",
                            component=FormComponent(type="eventTypes", props={"label": "Event types"})
                        ),
                        FormField(
                            id="debug",
                            name="Collect debugging information",
                            description="Set if you want to collect debugging information. Debugging collects a lot of "
                                        "data if you no longer need to test your workflow disable it to save data and "
                                        "compute power.",
                            component=FormComponent(type="bool", props={"label": "Collect debugging information"})
                        ),
                    ]
                ),
                FormGroup(
                    name="Debugging configuration",
                    description="In debug mode the following event will be injected into workflow.",
                    fields=[
                        FormField(
                            id="event_id",
                            name="Event ID",
                            description="Define event id. It may match the event that exists in database. "
                                        "If left empty random id will be generated.",
                            component=FormComponent(type="text", props={"label": "Event ID"})
                        ),
                        FormField(
                            id="event_type",
                            name="Event type",
                            description="Define event type. It may match the event that exists in database. "
                                        "If left empty then @debug-event-type will be defined.",
                            component=FormComponent(type="eventType", props={
                                "label": "Event type",
                                "onlyValueWithOptions": False
                            })
                        ),
                        FormField(
                            id="properties",
                            name="Event properties",
                            description="You can manually specify event properties for debug purpose. Works only for "
                                        "auto-generated events (does not work with the options below).",
                            component=FormComponent(type="json", props={"label": "Event types"})
                        ),
                        FormField(
                            id="profile_id",
                            name="Profile ID",
                            description="Define profile id. It may match the event that exists in database. "
                                        "If left empty random id will be generated.",
                            component=FormComponent(type="text", props={"label": "Profile ID"})
                        ),
                        FormField(
                            id="session_id",
                            name="Session ID",
                            description="Define session id. It may match the event that exists in database. "
                                        "If left empty random id will be generated.",
                            component=FormComponent(type="text", props={"label": "Session ID"})
                        ),
                    ]
                ),
            ]),
            version='0.8.0',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="start_action"
        ),
        metadata=MetaData(
            name='Start',
            desc='Starts workflow and returns event data on payload port.',
            keywords=['start node'],
            type="startNode",
            icon='event',
            width=200,
            height=200,
            group=["Flow"],
            purpose=['collection'],
            documentation=Documentation(
                inputs={},
                outputs={
                    "payload": PortDoc(desc="This port returns empty payload object.")
                }
            )
        )
    )
