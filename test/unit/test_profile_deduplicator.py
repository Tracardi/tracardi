import asyncio

from tracardi.domain.profile import Profile
from tracardi.service.profile_merger import ProfileMerger


def test_new_data_merging():
    async def main():
        profile = Profile(id="1")
        duplicate_profiles = [
            Profile(**{
                "id": profile.id,
                "data": {"pii": {"firstname": "Adam", "lastname": "Doe"}},
                "traits": {"custom": 1,
                           "A": 2,
                           "B": "A",
                           "C": [1],
                           "D": 1}
            }),
            Profile(**{
                "id": profile.id,
                "data": {"pii": {"lastname": None}},
                "traits": {"my-trait": 2,
                           "A": 3,
                           "B": "B",
                           "C": 2,
                           "D": [2]}
            })
        ]

        merger = ProfileMerger(profile)
        merged_profile, duplicates = await merger.deduplicate(duplicate_profiles)
        assert merged_profile.data.pii.firstname == 'Adam'
        assert merged_profile.data.pii.lastname == 'Doe'
        assert merged_profile.traits['custom'] == 1
        assert merged_profile.traits['my-trait'] == 2
        assert merged_profile.traits['A'] == 5
        assert merged_profile.traits['B'] == "B"
        assert merged_profile.traits['C'] == [1, 2]  # Here fails
        assert merged_profile.traits['D'] == [1, 2]

    asyncio.run(main())


def test_new_data_override_merging():
    async def main():
        profile = Profile(
            **{
                "id": "1",
                "data": {
                    "pii": {"firstname": "Adam", "lastname": "Doe", },
                    "devices": {"push": ['a', 'b', 'c']}
                },
                "traits": {"custom": 1}
            }
        )
        similar_profiles = [
            Profile(**{
                "id": profile.id,
                "data": {"pii": {"firstname": "Joe"}},
                "traits": {"custom": 2}
            }),
            Profile(**{
                "id": profile.id,
                "data": {"pii": {"lastname": "Bee"}},
                "traits": {"custom": 2}
            })
        ]

        merger = ProfileMerger(profile)
        merged_profile, duplicates = await merger.deduplicate(similar_profiles)

        assert merged_profile.data.pii.firstname == "Joe"
        assert merged_profile.data.pii.lastname == "Bee"
        assert merged_profile.traits['custom'] == 5
        assert set(merged_profile.data.devices.push) == {'a', 'b', 'c'}

    asyncio.run(main())
