from tracardi.domain.event import Event
from tracardi.domain.profile import Profile


def page_view(event: Event, profile: Profile):
    if profile.metadata.time.visit.count <= 1:
        return "awareness"
    return "consideration"


def session_opened(event: Event, profile: Profile):
    if profile.metadata.time.visit.count <= 1:
        return "awareness"
    return "consideration"
