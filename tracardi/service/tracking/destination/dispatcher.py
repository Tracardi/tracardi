from typing import Optional, List

from tracardi.config import tracardi
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.session import Session
from tracardi.service.destination.dispatchers import profile_destination_dispatch, event_destination_dispatch


async def sync_profile_destination(flat_profile: Optional[FlatProfile], changed_fields: List[dict]):
    has_profile = isinstance(flat_profile, FlatProfile)
    if has_profile and tracardi.enable_profile_destinations and flat_profile.has_not_saved_changes():
        await profile_destination_dispatch(
            flat_profile=flat_profile,
            changed_fields=changed_fields,
            debug=False,
            metadata={
                "source": "collector",
                "mode": "sync"
            }
        )


async def sync_event_destination(flat_profile: Optional[FlatProfile], session: Session, flat_events: List[FlatEvent],
                                 debug):
    if tracardi.enable_event_destinations and len(flat_events) > 0:
        await event_destination_dispatch(
            flat_profile,
            session,
            flat_events,
            debug,
            metadata={
                "source": "collector",
                "mode": "sync"
            }
        )
