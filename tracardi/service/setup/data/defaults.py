import os
from google.api_core.datetime_helpers import utcnow

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
    description="API Webhook collector"
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
    desctiprion="Internal event source for heartbeats.",
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
