from typing import Optional
from dotty_dict import Dotty
from tracardi.domain.profile import FlatProfile


def compute_ltcop(event: Dotty, profile: Optional[FlatProfile]):
    if profile:
        if 'data.metrics.ltcocc' in profile and 'data.metrics.ltcosc' in profile:
            if profile.get('data.metrics.ltcocc' ,0) == 0:
                return 0
            return profile['data.metrics.ltcosc']/profile['data.metrics.ltcocc']