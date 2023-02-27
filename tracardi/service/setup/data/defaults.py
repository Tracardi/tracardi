import os
from google.api_core.datetime_helpers import utcnow
from tracardi.service.plugin.domain.register import Form, FormGroup, FormField, FormComponent

from tracardi.config import tracardi
from tracardi.domain.bridge import Bridge
from tracardi.domain.event_source import EventSource
from tracardi.domain.named_entity import NamedEntity

_local_dir = os.path.dirname(__file__)

open_rest_source_bridge = Bridge(
    id="778ded05-4ff3-4e08-9a86-72c0195fa95d",
    type="rest",
    name="REST API Bridge",
    description="API /track collector"
)

open_webhook_source_bridge = Bridge(
    id="3d8bb87e-28d1-4a38-b19c-d0c1fbb71e22",
    type="webhook",
    name="API Webhook Bridge",
    description="API Webhook collector",
    config={
        "generate_profile": False,
        "replace_profile_id": ""
    },
    form=Form(groups=[
        FormGroup(
            name="Webhook configuration",
            description="A webhook typically gathers data without creating a profile or session. However, "
                        "if you want to create a profile and session for the collected data, you can set up the "
                        "configuration for it here.",
            fields=[
                FormField(
                    id="generate_profile",
                    name="Create profile and session for collected data.",
                    description="If you this turn on system will create a profile and session and attach it to event. "
                                "A profile and session are empty. You can add your own data to either "
                                "of them in the workflow.",
                    component=FormComponent(type="bool", props={"label": "Create profile and session"})
                ),
                FormField(
                    id="replace_profile_id",
                    name="Replace profile ID",
                    description="If you want to replace the Profile ID with data from the payload, reference the "
                                "data below or leave it empty if you don't want to create a profile or profile must "
                                "have random id. Make sure the Profile ID is secure and not easily guessable, as "
                                "easy profile IDs can lead to security issues.",
                    component=FormComponent(type="text", props={"label": "Replace profile"})
                )
            ])
])
)

with open(os.path.join(_local_dir, "manual/redirect_manual.md"), "r", encoding="utf-8") as fh:
    manual = fh.read()

redirect_bridge = Bridge(
    id='a495159f-91be-476d-a4e5-1b2d7e005403',
    type='redirect',
    name="Redirect URL Bridge",
    description=f"Redirects URLs and registers events.",
    manual=manual
)

cardio_event_source = EventSource(
    id=f"@{tracardi.cardio_source}",
    type=["internal"],
    name="Cardio Source",
    channel="Cardio",
    description="Internal event source for heartbeats.",
    bridge=NamedEntity(**open_rest_source_bridge.dict()),
    timestamp=utcnow(),
    tags=["internal"],
    groups=["Internal"]
)

default_db_data = {
    "bridge": [
        open_rest_source_bridge,
        open_webhook_source_bridge,
        redirect_bridge
    ],
    'event-source': [
        cardio_event_source
    ]
}
