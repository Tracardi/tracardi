from typing import Union

from tracardi.common.logging.log_handler import get_logger
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.profile import *
from tracardi.domain.storage_record import StorageRecord, StorageRecords
from tracardi.service.storage.elastic.driver.factory import storage_manager

logger = get_logger(__name__)


async def load_by_id(profile_id: str) -> Optional[StorageRecord]:
    query = {
        "size": 2,
        "query": {
            "bool": {
                "should": [
                    {
                        "term": {
                            "ids": profile_id
                        }
                    },
                    {
                        "term": {
                            "id": profile_id
                        }
                    }
                ],
                "minimum_should_match": 1
            }
        },
        "sort": [
            {
                "metadata.time.update": {
                    "order": "desc"
                }
            }
        ]
    }

    profile_records = await storage_manager('profile').query(query)

    if profile_records.total <= 0:
        return None

    if profile_records.total > 1:
        logger.warning(
            "Profile {} id duplicated in the database. It will be merged with APM worker.".format(profile_id))

    return profile_records.first()


async def load_all(start: int = 0, limit: int = 100, sort: List[Dict[str, Dict]] = None) -> StorageRecords:
    return await storage_manager('profile').load_all(start, limit, sort)


async def save(profile: Union[FlatProfile, Profile, List[Profile], Set[Profile]], refresh_after_save=False):
    if isinstance(profile, (list, set)):
        for _profile in profile:
            if isinstance(_profile, Profile):
                _profile.mark_for_update()
    elif isinstance(profile, Profile):
        profile.mark_for_update()
    result = await storage_manager('profile').upsert(profile, exclude={"operation": ...})
    if refresh_after_save:
        await storage_manager('profile').flush()
    return result


async def save_all(profiles: List[Profile]):
    return await storage_manager("profile").upsert(profiles, exclude={"operation": ...})
