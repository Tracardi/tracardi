from tracardi.domain.context import Context
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.domain.profile_traits import ProfileTraits
from tracardi_plugin_sdk.service.plugin_runner import run_plugin

from tracardi.process_engine.action.v1.strings.string_operations.plugin import StringOperatorActions

init = {"string": "event@id"}
payload = {}
profile = Profile(id="profile-id", traits=ProfileTraits(public={"test": "new test"}))
event = Event(id="event-id",
              type="event-type",
              profile=profile,
              session=Session(id="session-id"),
              source=Entity(id="source-id"),
              context=Context())
result = run_plugin(StringOperatorActions, init, payload,
                    profile, None, event)

print("OUTPUT:", result.output)
print("PROFILE:", result.profile)
