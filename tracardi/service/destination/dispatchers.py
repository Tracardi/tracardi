from typing import Optional, List, AsyncGenerator, Tuple

from tracardi.domain import ExtraInfo
from tracardi.domain.destination_work_package import DestinationWorkPackage
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.session import Session
from tracardi.exceptions.exception_service import get_traceback
from tracardi.exceptions.log_handler import get_logger
from tracardi.process_engine.destination.destination_interface import DestinationInterface
from tracardi.service.cache.destinations import load_profile_destinations, load_event_destinations
from tracardi.domain.destination import Destination
from tracardi.service.destination.utils import get_destination_data
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.utils.getters import get_entity_id

logger = get_logger(__name__)


async def yield_event_destination_work_package(flat_events: List[FlatEvent],
                                               flat_profile: Optional[FlatProfile] = None,
                                               session: Optional[Session] = None,
                                               ) -> AsyncGenerator[Tuple[FlatEvent, DestinationWorkPackage], None]:

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

            async for destination_work_package in get_destination_data(destinations, dot):
                yield flat_event, destination_work_package


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

            async for destination_work_package in get_destination_data(destinations, dot):

                destination_instance = destination_work_package.get_destination_instance(debug)  # type: DestinationInterface

                await destination_instance.dispatch_event(destination_work_package.data,
                                                          profile_id=get_entity_id(flat_profile),
                                                          session_id=get_entity_id(session),
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
                                       changed_fields: List[dict],
                                       debug: bool,
                                       metadata: dict = None):  # debug is used to find out which resource to use.

    dot = DotAccessor(flat_profile)
    destinations: List[Destination] = await load_profile_destinations()

    async for destination_work_package in get_destination_data(destinations, dot):
        try:
            destination_instance = destination_work_package.get_destination_instance(debug)  # type: DestinationInterface

            await destination_instance.dispatch_profile(
                destination_work_package.data,
                flat_profile=flat_profile,
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
