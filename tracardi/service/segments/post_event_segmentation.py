import logging
from typing import Callable

from tracardi.config import tracardi
from tracardi.domain.profile import Profile
from tracardi.domain.segment import Segment
from tracardi.domain.session import Session
from tracardi.exceptions.log_handler import log_handler
from tracardi.process_engine.tql.condition import Condition
from tracardi.service.notation.dot_accessor import DotAccessor
from tracardi.service.segments.segment_trigger import trigger_segment_workflow

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


async def _segment(profile, session, event_types, load_segments):
    """
    This method mutates current profile. Loads segments and adds segments to current profile.
    """

    # todo cache segments for 30 sec
    flat_profile = DotAccessor(
        profile=profile
        # it has access only to profile. Other data is irrelevant because we check only profile.
    )

    for event_type in event_types:  # type: str

        # Segmentation is run for every event

        # todo segments are loaded one by one - maybe it is possible to load it at once
        # todo segments are loaded event if they are disabled. It is checked later. Maybe we can filter it here.
        segments = await load_segments(event_type, limit=500)

        for segment in segments:

            segment = Segment(**segment)

            if segment.enabled is False:
                continue

            segment_id = segment.get_id()

            try:
                condition = Condition()
                if await condition.evaluate(segment.condition, flat_profile):
                    segments = set(profile.segments)
                    segments.add(segment_id)
                    profile.segments = list(segments)
                    # This needs to be done to trigger workflow. Segment is already added to the profile
                    trigger_segment_workflow(profile, session, segment_id)

                    # Yield only if segmentation triggered
                    yield event_type, segment_id, None

            except Exception as e:
                msg = 'Condition id `{}` could not evaluate `{}`. The following error was raised: `{}`'.format(
                    segment_id, segment.condition, str(e).replace("\n", " "))

                yield event_type, segment_id, msg


async def post_ev_segment(profile: Profile, session: Session, event_types: list, load_segments: Callable) -> dict:
    """
    This is Post Event Segmentation
    """

    segmentation_result = {"errors": [], "ids": []}
    try:
        # Segmentation
        if profile.operation.needs_update() or profile.operation.needs_segmentation():
            # Segmentation runs only if profile was updated or flow forced it
            async for event_type, segment_id, error in _segment(
                    profile,
                    session,
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
