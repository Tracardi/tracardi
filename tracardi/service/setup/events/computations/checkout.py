from tracardi.domain.event import Event


def compute_ltcop(event: Event, profile: dict):
    if 'data.metrics.ltcocc' in profile and 'data.metrics.ltcosc' in profile:
        if profile['data.metrics.ltcocc'] == 0:
            return 0
        return profile['data.metrics.ltcosc']/profile['data.metrics.ltcocc']