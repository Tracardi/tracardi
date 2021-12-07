from tracardi.domain.context import Context
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi_plugin_sdk.service.plugin_runner import run_plugin

from tracardi_event_counter.plugin import EventCounter

init = {"event_type": "page-view", "time_span": "-1h30min"}
payload = {}
profile = Profile(id="profile-id")
event = Event(id="event-id",
              type="event-type",
              profile=profile,
              session=Session(id="session-id"),
              source=Entity(id="source-id"),
              context=Context())
result = run_plugin(EventCounter,
                    init,
                    payload,
                    profile,
                    event=event)

print("OUTPUT:", result.output)
print("PROFILE:", result.profile)
