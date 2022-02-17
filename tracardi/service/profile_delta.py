from deepdiff import DeepDiff

from tracardi.domain.profile import Profile
from tracardi.domain.profile_traits import ProfileTraits


def get_profile_delta(profile1, profile2):
    return profile1 == profile2


if __name__ == "__main__":
    profile1 = Profile(id="1", traits=ProfileTraits(public={"a": ["1","2"], "b": "2"}))
    profile2 = Profile(id="1", traits=ProfileTraits(public={"b": "2", "a": ["2","1"]}))

    diff = DeepDiff(profile1.dict(), profile2.dict(), ignore_order=True)
    print(diff)
