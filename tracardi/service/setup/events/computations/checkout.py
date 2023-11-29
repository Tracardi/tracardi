from dotty_dict import Dotty


def compute_ltcop(event: Dotty, profile: Dotty):
    if 'data.metrics.ltcocc' in profile and 'data.metrics.ltcosc' in profile:
        if profile.get('data.metrics.ltcocc' ,0) == 0:
            return 0
        return profile['data.metrics.ltcosc']/profile['data.metrics.ltcocc']