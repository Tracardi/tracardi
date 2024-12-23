from typing import Optional

from tracardi.domain.flat_profile import FlatProfile
from tracardi.service.dotdict import DotDict


def page_view(event: DotDict, profile: Optional[FlatProfile]):
    if profile:
        if profile.get('metadata.time.visit.count', 0) <= 1:
            return "awareness"
        return "consideration"


def session_opened(event: DotDict, profile: Optional[FlatProfile]):
    if profile:
        if profile.get('metadata.time.visit.count',0) <= 1:
            return "awareness"
        return "consideration"
