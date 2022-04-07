import asyncio
import json

from tracardi.domain.api_instance import ApiInstance
from tracardi.domain.entity import Entity
from tracardi.domain.event_metadata import EventPayloadMetadata
from tracardi.domain.payload.event_payload import EventPayload
from tracardi.domain.payload.tracker_payload import TrackerPayload
from tracardi.domain.time import Time
from tracardi.process_engine.action.v1.flow.postpone_event.model.configuration import Configuration
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.postpone_call import PostponedCall
from tracardi.service.tracker import synchronized_event_tracking


def validate(config: dict):
    return Configuration(**config)


class PostponeEventAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def _postponed_run(self):
        ip = self.event.context['ip'] if 'ip' in self.event.context else 'http://localhost'
        tracker_payload = TrackerPayload(
            source=Entity(id=self.event.source.id),
            session=Entity(id=self.session.id),
            profile=Entity(id=self.profile.id),
            context={},
            properties={},
            events=[
                EventPayload(
                    type=self.config.event_type,
                    properties=json.loads(self.config.event_properties),
                    context=self.event.context
                )
            ],
            metadata=EventPayloadMetadata(
                time=Time(),
                ip=ip
            )
        )
        await synchronized_event_tracking(tracker_payload, host="http://localhost", profile_less=False)

    async def run(self, payload):
        postponed_call = PostponedCall(
            self.profile.id,
            self._postponed_run,
            ApiInstance().id
        )
        postponed_call.wait = self.config.delay
        postponed_call.run(asyncio.get_running_loop())
        return None


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='PostponeEventAction',
            author="Risto Kowaczewski",
            inputs=["payload"],
            outputs=[],
            version="0.6.2",
            init={
                'event_type': '',
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
            manual=None
        ),
        metadata=MetaData(
            name='Delayed event',
            desc='Raise event that is delayed X seconds after the customer visit ends.',
            icon='event',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload object.")
                },
                outputs={}
            ),
            emits_event={
                "x": "Defined in plugin"
            }
        )
    )
