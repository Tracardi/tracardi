from tracardi.domain.context import Context
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi_plugin_sdk.service.plugin_runner import run_plugin

from tracardi_regex_match.plugin import SearchAction

init = {
    "pattern": r"(\b[A-Z]+\b).+(\b\d+)",
    "text":  "The price of PINEAPPLE ice cream is 20",
    "groups": ["group A", "group B"]}
payload = {}
profile = Profile(id="profile-id")
event = Event(id="event-id",
              type="event-type",
              profile=profile,
              session=Session(id="session-id"),
              source=Entity(id="source-id"),
              context=Context())
result = run_plugin(SearchAction, init, payload,
                    profile)

print("OUTPUT:", result.output)
print("PROFILE:", result.profile)
