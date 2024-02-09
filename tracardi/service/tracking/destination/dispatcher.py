import logging
from typing import Optional

from tracardi.domain import ExtraInfo
from tracardi.service.cache_manager import CacheManager

from tracardi.config import tracardi
from tracardi.domain.console import Console
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.exceptions.exception_service import get_traceback
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.console_log import ConsoleLog
from tracardi.service.destinations.dispatchers import profile_destination_dispatch
from tracardi.service.utils.getters import get_entity_id

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)
cache = CacheManager()

async def sync_destination(profile: Optional[Profile], session: Session, console_log: ConsoleLog):
    has_profile = isinstance(profile, Profile)
    if has_profile:
        if has_profile:
            try:
                load_destination_task = cache.profile_destinations
                await profile_destination_dispatch(load_destination_task,
                                                   profile=profile,
                                                   session=session,
                                                   debug=False)
            except Exception as e:
                # todo - this appends error to the same profile - it rather should be en event error
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