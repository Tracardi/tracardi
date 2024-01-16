from typing import Optional

from dotty_dict import Dotty

from tracardi.domain.profile import FlatProfile


def page_view(event: Dotty, profile: Optional[FlatProfile]):
    if profile:
        if profile.get('metadata.time.visit.count', 0) <= 1:
            return "awareness"
        return "consideration"


def session_opened(event: Dotty, profile: Optional[FlatProfile]):
    if profile:
        if profile.get('metadata.time.visit.count',0) <= 1:
            return "awareness"
        return "consideration"
