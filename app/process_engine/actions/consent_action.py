# from app.domain.action import ActionEvaluator
from app.domain.payload.event_payload import EventPayload
from app.domain.payload.tracker_payload import TrackerPayload
from app.domain.user_consent import UserConsent


class ConsentAction:

    async def run(self, payload: TrackerPayload, event: EventPayload, config: dict):
        consent = UserConsent(**event.properties)
        payload.profile.consents[consent.id] = consent
        return payload.profile
