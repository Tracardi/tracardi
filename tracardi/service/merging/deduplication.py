from typing import Optional

from tracardi.domain.profile import Profile
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.license import License, LICENSE
from tracardi.service.merging.facade_old import deduplicate_profile
from tracardi.service.merging.status import NO_LOCK_ACQUIRED, MERGED
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis.driver.redis_client import RedisClient
from tracardi.service.tracking.locking import async_mutex, Lock, DONE_WAITING
from tracardi.service.utils.getters import get_entity_id


if License.has_service(LICENSE):
    from com_tracardi.service.merging.facade import compute_one_profile_in_db

logger = get_logger(__name__)

async def deduplicate(profile: Profile, profile_pk: Optional[str]=None):
        _redis = RedisClient()

        key = Lock.get_key(Collection.lock_tracker, "profile", get_entity_id(profile))
        lock = Lock(_redis, key, default_lock_ttl=30)  # Lock is kept for 30 sec

        # It breaks after 5 sec of waiting
        async with async_mutex(lock, name='profile_merging_worker', break_after_time=30) as prev_lock_status:

            if prev_lock_status == DONE_WAITING:
                logger.info(f"Skipped deduplication of {profile.id}. Will be done in next round.")
                return NO_LOCK_ACQUIRED

            if License.has_service(LICENSE):
                logger.info(f"Commercial merging invoked for profile id `{profile.id}`.")
                return await compute_one_profile_in_db(profile, profile_pk=profile_pk)

            else:
                logger.info("Open-source merging invoked.")
                await deduplicate_profile(profile.id, profile.ids)
                return MERGED
