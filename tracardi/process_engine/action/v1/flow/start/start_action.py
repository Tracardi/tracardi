from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.configuration import Configuration
from tracardi.service.storage.driver import storage
from datetime import datetime
from tracardi.service.wf.domain.graph_invoker import GraphInvoker
from typing import Tuple, Optional
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
import json
from json import JSONDecodeError
from tracardi.service.storage.factory import StorageFor
from tracardi.domain.entity import Entity


def validate(config: dict):
    return Configuration(**config)


class StartAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def _create_full_event(self, event_data) -> Tuple[Event, Optional[Profile], Optional[Session]]:

        session = None
        profile = None
        event = Event(**event_data)
        event.metadata.profile_less = self.config.profile_less

        # Do it only for made-up events - when no event ID and event type is specified
        if (not self.config.event_id) and not (self.config.event_type and self.config.event_type.id):
            try:
                event.properties = json.loads(self.config.properties)
            except JSONDecodeError as e:
                self.console.warning(str(e))

        if event.session is not None:
            session = await storage.driver.session.load_by_id(event.session.id)

        if self.config.profile_less is False and isinstance(event.profile, Entity):
            profile_entity = Entity(id=event.profile.id)
            profile = await StorageFor(profile_entity).index('profile').load(Profile)  # type: Optional[Profile]

        if self.config.profile_less is False and isinstance(event.profile, Entity) and profile is None:
            raise ValueError(
                "Event type '{}' has reference to empty profile id '{}'. Debug stopped. This event is corrupted.".format(
                    event.id, event.profile.id))

        return event, profile, session

    async def debug_run(self):
        if self.config.event_id:
            event = await storage.driver.event.load(self.config.event_id)
            if event is None:
                raise ValueError(
                    f"There is no event with ID '{self.config.event_id}'. Check configuration of start node."
                )
            events = [event]

        elif self.config.event_type is not None and self.config.event_type.id:
            result = await storage.driver.event.load_event_by_type(self.config.event_type.id, limit=10)
            if result.total == 0:
                raise ValueError(
                    f"There is no event with type '{self.config.event_type.id}'. Check configuration for event type."
                )
            events = list(result)

        else:
            events = [
                {
                    "id": "@debug-event-id",
                    "metadata": {
                        "time": {
                            "insert": datetime.utcnow()
                        },
                        "ip": "127.0.0.1",
                        "profile_less": True
                    },
                    "source": {
                        "id": "debug-source"
                    },
                    "type": "debug-event-type",
                    "properties": {},
                    "context": {
                        "config": {
                            "debugger": True
                        },
                        "params": {}
                    }
                }
            ]

        for event_data in events:

            try:

                event, profile, session = await self._create_full_event(event_data)

                if self.event is not None:
                    self.event.replace(event)
                else:
                    self.event = event
                self.event.metadata.debug = True
                self.event.session = session
                self.event.source = event.source

                # Session can be None is user requested not to save it.
                if self.config.session_less is True or session is None:
                    self.event.session = None
                    self.session = None

                    # Remove session in all nodes because the event is session less
                    graph = self.execution_graph  # type: GraphInvoker
                    if isinstance(graph, GraphInvoker):
                        graph.set_sessions(None)

                elif self.session is not None:
                    self.session.replace(session)

                # Event can be profile less if collected via webhook
                if self.config.profile_less is True:
                    self.event.profile = None
                    self.profile = None

                    # Remove profiles in all nodes because the event is profile less
                    graph = self.execution_graph  # type: GraphInvoker
                    if isinstance(graph, GraphInvoker):
                        graph.set_profiles(None)
                else:
                    if self.profile is not None and profile is not None:
                        self.profile.replace(profile)

                return Result(port="payload", value=self.event.dict())

            except ValueError as e:
                self.console.warning(str(e))

        raise ValueError(
            f"There is no event that is consistent in terms of current configuration. See log error for details."
        )

    async def production_run(self):
        self.event.metadata.debug = self.config.debug

        allowed_event_types = self.config.get_allowed_event_types()

        if len(allowed_event_types) > 0 and self.event.type not in self.config.get_allowed_event_types():
            return None

        return Result(port="payload", value=self.event.dict())

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
                "profile_less": False,
                "session_less": False,
                "properties": "{}",
                "event_id": None,
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
                            id="profile_less",
                            name="Profile-less event",
                            description="Profile-less events are events that does not attach profile data.",
                            component=FormComponent(type="bool", props={"label": "Profile-less event"})
                        ),
                        FormField(
                            id="session_less",
                            name="Session-less event",
                            description="Session-less events may occur when user did not want session to be saved.",
                            component=FormComponent(type="bool", props={"label": "Session-less event"})
                        ),
                        FormField(
                            id="properties",
                            name="Event properties",
                            description="You can manually specify event properties for debug purpose. Works only for "
                                        "auto-generated events (does not work with the options below).",
                            component=FormComponent(type="json", props={"label": "Event types"})
                        ),
                        FormField(
                            id="event_id",
                            name="Event ID",
                            description="You can load event by its id for debug purpose. This field is optional. "
                                        "If provided than id takes precedence before event type.",
                            component=FormComponent(type="text", props={"label": "Event ID"})
                        ),
                        FormField(
                            id="event_type",
                            name="Event type",
                            description="You can load event of selected type in debug mode. If left empty, generates "
                                        "debug-event-type event or loads event by id if provided.",
                            component=FormComponent(type="eventType", props={"label": "Event type"})
                        ),
                    ]
                ),
            ]),
            version='0.6.1',
            license="MIT",
            author="Risto Kowaczewski",
            manual="start_action"
        ),
        metadata=MetaData(
            name='Start',
            desc='Starts workflow and returns event data on payload port.',
            keywords=['start node'],
            type="startNode",
            icon='start',
            width=200,
            height=200,
            group=["Flow"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={},
                outputs={
                    "payload": PortDoc(desc="This port returns empty payload object.")
                }
            )
        )
    )
