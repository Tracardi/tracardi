import logging
from typing import Callable

from tracardi.config import tracardi
from tracardi.domain.profile import Profile
from tracardi.exceptions.log_handler import log_handler

logger = logging.getLogger("Segmentation")
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def segment(profile: Profile, event_types: list, load_segments: Callable) -> dict:
    segmentation_result = {"errors": [], "ids": []}
    try:
        # Segmentation
        if profile.operation.needs_update() or profile.operation.needs_segmentation():
            # Segmentation runs only if profile was updated or flow forced it
            async for event_type, segment_id, error in profile.segment(
                    event_types,
                    load_segments):
                # Segmentation triggered
                if error:
                    segmentation_result['errors'].append(error)
                segmentation_result['ids'].append(segment_id)
    except Exception as e:
        # this error is a global segmentation error
        # todo log it.
        logger.error(str(e))
    finally:
        return segmentation_result
