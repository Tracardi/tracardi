from tracardi.domain.pii import PII
from tracardi.domain.profile import Profile, Profiles
from tracardi.domain.profile_stats import ProfileStats


def test_profile_merge():
    p1 = Profile(
        id="1",
        stats=ProfileStats(views=1, visits=2),
        traits={
            "private": {
                "a": 1,
                "b": 2
            },
            "public": {
                "a": 1,
                "b": 2
            }
        },
        pii=PII(
            name="john",
            surname="doe"
        ),
        segments=['segment-1'],
        consents={"all": "granted"}
    )

    p2 = Profile(
        id="2",
        stats=ProfileStats(views=2, visits=4),
        traits={
            "private": {
                "a": 2,
                "c": 1
            }
        },
        pii=PII(
            name="jonathan",
            surname="doe"
        )
    )

    p3 = Profile(
        id="3",
        traits={
            "private": {
                "a": [3],
                "c": 1
            },
            "public": {
                "a": 1,
                "b": 3
            }
        },
        segments=['segment-2'],
        consents={"all": "not-granted"}
    )

    profiles = [p1, p2]
    p = Profiles.merge(profiles, p3)

    assert p.consents == {'all': 'not-granted'}
    assert p.traits.private == {'b': 2, 'a': [1, 2, 3], 'c': 1}
    assert p.traits.public == {'b': [2, 3], 'a': 1}
    assert set(p.pii.name).intersection({'john', 'jonathan'}) == {'john', 'jonathan'}
    assert p.pii.surname == 'doe'
    assert p.mergedWith is None
    assert p.stats.views == 3
    assert p.stats.visits == 6
