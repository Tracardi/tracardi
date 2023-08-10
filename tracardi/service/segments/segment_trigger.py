from typing import List, Union

from com_worker.trigger.worker import trigger_workflow_with_added_segment
from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.license import License, LICENSE


def _add_segment(profile: Profile, session: Session, segment: str):
    profile.segments.append(segment)
    if License.has_service(LICENSE) and tracardi.enable_segmentation_wf_triggers:
        context = get_context()
        trigger_workflow_with_added_segment(context.dict(),
                                            profile.dict(exclude={"operation": ...}),
                                            session.dict(exclude={"operation": ...}),
                                            segment)
        print("Trigger by segmentation")


def trigger_segment_add(profile: Profile, session: Session, segments: Union[List[str], str]):
    if isinstance(segments, list):
        for segment in segments:
            _add_segment(profile, session, segment)

    elif isinstance(segments, str):
        _add_segment(profile, session, segments)

