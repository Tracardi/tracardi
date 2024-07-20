import logging
from typing import Optional, List

from tracardi.config import tracardi
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.destination.dispatchers import profile_destination_dispatch, event_destination_dispatch

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def sync_profile_destination(profile: Optional[Profile], session: Session, changed_fields: List[dict]):
    has_profile = isinstance(profile, Profile)
    if has_profile and tracardi.enable_profile_destinations and profile.has_not_saved_changes():
        await profile_destination_dispatch(
            profile=profile,
            session=session,
            changed_fields=changed_fields,
            debug=False,
            metadata={
                "source": "collector",
                "mode": "sync"
            }
        )


async def sync_event_destination(profile: Optional[Profile], session: Session, events: List[Event], debug):
    if tracardi.enable_event_destinations and len(events) > 0:
        await event_destination_dispatch(
            profile,
            session,
            events,
            debug,
            metadata={
                "source": "collector",
                "mode": "sync"
            }
        )
