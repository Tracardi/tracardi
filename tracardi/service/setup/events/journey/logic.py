from dotty_dict import Dotty


def page_view(event: Dotty, profile: Dotty):
    if profile.get('metadata.time.visit.count', 0) <= 1:
        return "awareness"
    return "consideration"


def session_opened(event: Dotty, profile: Dotty):
    if profile.get('metadata.time.visit.count',0) <= 1:
        return "awareness"
    return "consideration"
