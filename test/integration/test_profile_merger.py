import asyncio

from tracardi.domain.profile import Profile
from tracardi.service.profile_merger import ProfileMerger


def test_merging():

    async def main():
        profile = Profile(id="1")
        similar_profiles = [
            Profile(**{"id": profile.id, "data": {"pii": {"firstname": "Adam"}}})
        ]

        merger = ProfileMerger(profile)
        merged_profile, duplicates = await merger.deduplicate(similar_profiles)
        print(merged_profile)
        assert merged_profile.data.pii.firstname == 'Adam'

    asyncio.run(main())