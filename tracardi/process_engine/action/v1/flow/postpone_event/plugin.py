import asyncio
import json
from typing import Tuple

from tracardi.domain.api_instance import ApiInstance
from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.settings import Settings
from tracardi.domain.time import Time
from tracardi.process_engine.action.v1.flow.postpone_event.model.configuration import Configuration
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.postpone_call import PostponedCall
from tracardi.service.tracker import track_event


def validate(config: dict):
    return Configuration(**config)


class PostponeEventAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        if self.profile is None:
            self.console.error("PostponeEventAction: Profile less events can not be delayed.")
            return None

        dot = self._get_dot_accessor(payload)
        converter = DictTraverser(dot)
        event_properties = converter.reshape(json.loads(self.config.event_properties))

        async def _postponed_run():
            ip = self.event.request['ip'] if 'ip' in self.event.request else '127.0.0.1'

            if self.config.source.id == "":
                even_source_id = self.event.source.id
            else:
                even_source_id = self.config.source.id

            tracker_payload = TrackerPayload(
                source=Entity(id=even_source_id),
                session=Entity(id=self.session.id),
                profile=Entity(id=self.profile.id),
                context={},
                properties={},
                events=[
                    EventPayload(
                        type=self.config.event_type,
                        properties=event_properties,
                        context=self.event.context
                    )
                ],
                metadata=EventPayloadMetadata(
                    time=Time(),
                    ip=ip
                )
            )
            await track_event(tracker_payload,
                              ip="http://localhost",
                              allowed_bridges=['rest'])

        postponed_call = PostponedCall(
            self.profile.id,
            _postponed_run,
            ApiInstance().id
        )
        postponed_call.wait = self.config.delay
        postponed_call.run(asyncio.get_running_loop())
        return None


def register() -> Tuple[Plugin, Settings]:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='PostponeEventAction',
            author="Risto Kowaczewski",
            license="Tracardi Pro License",
            inputs=["payload"],
            outputs=[],
            version="0.6.2",
            manual=None,
            init={
                'event_type': '',
                'source': {
                    'id': '',
                    'name': ''
                },
                'event_properties': '{}',
                'delay': 60
            },
            form=Form(groups=[
                FormGroup(
                    name="Event delay",
                    description="Define when the even should be raised.",
                    fields=[
                        FormField(
                            id="delay",
                            name="Delay",
                            description="Type number of seconds that the event should be postponed after the visit ends. "
                                        "We consider that visit ends if there is no new event after X seconds. "
                                        "Delay is the X variable in this "
                                        "algorithm.",
                            component=FormComponent(type="text", props={"label": "Delay in seconds"})
                        )
                    ]
                ),
                FormGroup(
                    name="Event details",
                    description="Define event type and properties that will be rend to the system.",
                    fields=[
                        FormField(
                            id="source",
                            name="Event source",
                            description="Select where to send delayed event. What event source to use.",
                            component=FormComponent(type="source", props={"label": "Event source"})
                        ),
                        FormField(
                            id="event_type",
                            name="Raise event type",
                            description="Type event type you would like to raise.",
                            component=FormComponent(type="text", props={"label": "Event type"})
                        ),
                        FormField(
                            id="event_properties",
                            name="Event properties",
                            description="Type additional properties to be sent with event. Event will fire within the "
                                        "current profile context and with current session.",
                            component=FormComponent(type="json", props={"label": "Event properties"})
                        ),
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Delayed event',
            desc='Raise event that is delayed X seconds after the customer visit ends.',
            icon='event',
            group=["Operations"],
            tags=['pro', 'scheduler', 'schedule'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload object.")
                },
                outputs={}
            ),
            emits_event={
                "Delayed event": "delayed-event"
            },
            pro=True
        )
    ), Settings(hidden=True)
