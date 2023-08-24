from typing import List, Union
from tracardi.config import tracardi
from tracardi.context import get_context
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi.service.license import License, LICENSE
if License.has_service(LICENSE) and tracardi.enable_segmentation_wf_triggers:
    from com_worker.trigger.worker import trigger_workflow_with_added_segment


def trigger_segment_workflow(profile: Profile, session: Session, segment: str):
    if License.has_service(LICENSE) and tracardi.enable_segmentation_wf_triggers:
        context = get_context()
        trigger_workflow_with_added_segment(context.dict(),
                                            profile.dict(exclude={"operation": ...}),
                                            session.dict(exclude={"operation": ...}),
                                            segment)
        print("Trigger by segmentation")


def trigger_segment_add(profile: Profile, session: Session, segments: Union[List[str], str]) -> Profile:
    if isinstance(segments, list):
        for segment in segments:
            profile.segments.append(segment)
            trigger_segment_workflow(profile, session, segment)

    elif isinstance(segments, str):
        profile.segments.append(segments)
        trigger_segment_workflow(profile, session, segments)

    return profile

