from tracardi.domain.context import Context
from tracardi.domain.entity import Entity
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi_plugin_sdk.service.plugin_runner import run_plugin
from datetime import datetime
from tracardi.process_engine.action.v1.consents.add_consent_action.plugin import ConsentAdder

init = {
    "consents": "payload@consents"
}
payload = {
    "consents": {
        "marketing-consent": {"revoke": datetime.utcnow()},
        "no-consent": {"revoke": datetime.utcnow()}
    }
}
profile = Profile(id="profile-id")
event = Event(id="event-id",
              type="event-type",
              profile=profile,
              session=Session(id="session-id"),
              source=Entity(id="source-id"),
              context=Context())
result = run_plugin(ConsentAdder, init, payload,
                    profile)

print("OUTPUT:", result.output)
print("PROFILE:", result.profile)