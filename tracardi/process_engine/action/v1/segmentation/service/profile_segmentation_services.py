from typing import Union, List

from tracardi.domain.profile import Profile


def add_segment_to_profile(profile: Profile, segments: Union[List[str], str]) -> Profile:
    if isinstance(segments, list):
        for segment in segments:
            profile.segments.append(segment)

    elif isinstance(segments, str):
        profile.segments.append(segments)

    return profile
