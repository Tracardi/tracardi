import asyncio
from typing import List, Tuple, Optional, Set

from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.storage_record import RecordMetadata, StorageRecords
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.storage.elastic.driver.factory import storage_manager
from tracardi.service.storage.elastic.interface.collector.mutation import profile as mutation_profile_db

logger = get_logger(__name__)
_max_load_chunk = 1000


async def _load_profile_duplicates(profile_ids: Set[str]) -> StorageRecords:
    return await storage_manager('profile').query({
        "size": _max_load_chunk,
        "query": {
            "bool": {
                "should": [
                    {
                        "terms": {
                            "ids": list(profile_ids)
                        }
                    },
                    {
                        "terms": {
                            "id": list(profile_ids)
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "sort": [
            {"metadata.time.insert": "asc"}  # todo maybe should be based on updates (but update should always exist)
        ]
    })


async def _load_duplicated_profiles_with_merge_key(merge_by: List[Tuple[str, str]]) -> StorageRecords:
    return await storage_manager('profile').load_by_values(
        merge_by,
        condition='must',
        limit=_max_load_chunk)


async def delete_multiple_profiles(profile_tuples: List[Tuple[str, RecordMetadata]]):
    tasks = [asyncio.create_task(mutation_profile_db.delete_profile(profile_id, metadata.index))
             for profile_id, metadata in profile_tuples]
    return await asyncio.gather(*tasks)



async def save_merged_flat_profile(flat_profile: FlatProfile):
    # Auto refresh db
    await mutation_profile_db.save_flat_profile(flat_profile, refresh=True)


async def save_marked_for_merge_profiles(flat_profiles: List[FlatProfile]):
    # Convert to profiles
    # TODO EOFP - End of FlatProfile
    profiles = [flat_profile.as_profile() for flat_profile in flat_profiles]
    await mutation_profile_db.save_profiles_in_db(profiles)
