from typing import Optional, List

from tracardi.domain import ExtraInfo
from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.exception_service import get_traceback
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache.destinations import load_profile_destinations, load_event_destinations
from tracardi.domain.destination import Destination
from tracardi.service.destination.utils import get_dispatch_destination_and_data
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.utils.getters import get_entity_id

logger = get_logger(__name__)


async def event_destination_dispatch(profile: Optional[Profile],
                                     session: Optional[Session],
                                     events: List[Event],
                                     debug):
    dot = DotAccessor(profile, session)
    for event in events:
        try:
            # Reads from cache
            destinations: List[Destination] = await load_event_destinations(
                event.type,
                event.source.id
            )

            dot.set_storage("event", event)

            result = await get_dispatch_destination_and_data(
                dot, destinations, debug
            )

            if result is None:
                # No destination found
                return

            destination_instance, reshaped_data = result

            await destination_instance.dispatch_event(reshaped_data, profile=profile, session=session, event=event)
        except Exception as e:
            logger.error(
                str(e),
                extra=ExtraInfo.exact(
                    flow_id=None,
                    node_id=None,
                    event_id=get_entity_id(event),
                    profile_id=get_entity_id(profile),
                    origin='profile-destination',
                    package=__name__,
                    traceback=get_traceback(e)
                )
            )

async def profile_destination_dispatch(profile: Optional[Profile],
                                       session: Optional[Session],
                                       changed_fields: List[dict],
                                       debug: bool):  # debug is used to find out which resource to use.

    dot = DotAccessor(profile, session)
    destinations: List[Destination] = await load_profile_destinations()

    result = await get_dispatch_destination_and_data(
        dot, destinations, debug
    )

    if result is None:
        # No destination found
        return

    destination_instance, reshaped_data = result
    try:
        logger.info(f"Dispatching {result}. Profile id: {get_entity_id(profile)}.")
        await destination_instance.dispatch_profile(reshaped_data, profile=profile, session=session, changed_fields=changed_fields)
    except Exception as e:
        logger.error(
            str(e),
            extra=ExtraInfo.exact(
                flow_id=None,
                node_id=None,
                event_id=None,
                profile_id=get_entity_id(profile),
                origin='profile-destination',
                package=__name__,
                traceback=get_traceback(e)
            )
        )

