from tracardi.domain.time import Time

from tracardi.domain.context import Context
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.event_metadata import EventMetadata
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.process_engine.action.v1.converters.payload_to_json.plugin import ConvertAction
from tracardi_plugin_sdk.service.plugin_runner import run_plugin

init = {
    "to_json": "event@..."
}
payload = {}
profile = Profile(id="profile-id")
event = Event(metadata=EventMetadata(time=Time()),
              id="event-id",
              type="event-type",
              profile=profile,
              session=Session(id="session-id"),
              source=Entity(id="source-id"),
              context=Context())
result = run_plugin(ConvertAction, init, payload,
                    profile, event=event)

print("OUTPUT:", result.output)
print("PROFILE:", result.profile)
