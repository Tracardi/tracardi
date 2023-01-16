from tracardi.domain.profile import Profile


def test_profile_must_have_id_in_ids():
    profile = Profile(id="1")
    assert profile.id in profile.ids
