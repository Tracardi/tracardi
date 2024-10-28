from typing import Optional, List

from tracardi.domain import ExtraInfo
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.session import Session
from tracardi.exceptions.exception_service import get_traceback
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.cache.destinations import load_profile_destinations, load_event_destinations
from tracardi.domain.destination import Destination
from tracardi.service.destination.utils import get_dispatch_destination_and_data
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.utils.getters import get_entity_id

logger = get_logger(__name__)


async def event_destination_dispatch(flat_profile: Optional[FlatProfile],
                                     session: Optional[Session],
                                     flat_events: List[FlatEvent],
                                     debug,
                                     metadata=None
                                     ):
    dot = DotAccessor(flat_profile, session)
    for flat_event in flat_events:

        try:
            # Reads from cache
            destinations: List[Destination] = await load_event_destinations(
                flat_event.type,
                flat_event.get('source.id')
            )

            if not destinations:
                continue

            dot.set_storage("event", flat_event)

            async for destination_instance, reshaped_data in get_dispatch_destination_and_data(
                    dot,
                    destinations,
                    debug):
                await destination_instance.dispatch_event(reshaped_data,
                                                          flat_profile=flat_profile,
                                                          session=session,
                                                          flat_event=flat_event,
                                                          metadata=metadata)
        except Exception as e:
            logger.error(
                str(e),
                extra=ExtraInfo.exact(
                    flow_id=None,
                    node_id=None,
                    event_id=get_entity_id(flat_event),
                    profile_id=get_entity_id(flat_profile),
                    origin='profile-destination',
                    package=__name__,
                    traceback=get_traceback(e)
                )
            )


async def profile_destination_dispatch(flat_profile: Optional[FlatProfile],
                                       session: Optional[Session],
                                       changed_fields: List[dict],
                                       debug: bool,
                                       metadata: dict = None):  # debug is used to find out which resource to use.

    dot = DotAccessor(flat_profile, session)
    destinations: List[Destination] = await load_profile_destinations()

    async for destination_instance, reshaped_data in get_dispatch_destination_and_data(dot, destinations, debug):
        try:
            logger.info(f"Dispatching {destination_instance}. Profile id: {get_entity_id(flat_profile)}.")
            await destination_instance.dispatch_profile(
                reshaped_data,
                flat_profile=flat_profile,
                session=session,
                changed_fields=changed_fields,
                metadata=metadata
            )
        except Exception as e:
            logger.error(
                str(e),
                extra=ExtraInfo.exact(
                    flow_id=None,
                    node_id=None,
                    event_id=None,
                    profile_id=get_entity_id(flat_profile),
                    origin='profile-destination',
                    package=__name__,
                    traceback=get_traceback(e)
                )
            )
