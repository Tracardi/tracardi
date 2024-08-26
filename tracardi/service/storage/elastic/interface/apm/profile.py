from typing import AsyncGenerator, Any, Tuple

from tracardi.domain.profile import Profile
from tracardi.exceptions.log_handler import get_logger

from tracardi.service.storage.elastic.dal.profile import _load_profiles_for_auto_merge, \
    _get_duplicated_profiles_by_field, _get_profiles_by_field_and_value, \
    _load_by_id, _aggr_profiles_with_duplicated_ids

logger = get_logger(__name__)


async def load_profiles_for_auto_merge() -> AsyncGenerator[Profile, Any]:
    async for profile_record in _load_profiles_for_auto_merge():
        yield profile_record.to_entity(Profile)


async def load_profiles_with_duplicated_ids(log_error=True) -> AsyncGenerator[Profile, Any]:
    records = await _aggr_profiles_with_duplicated_ids(log_error)

    duplicated_ids = set()
    for data in records.aggregations("duplicate_ids").buckets():
        logger.info(f"Found {data['doc_count']} profiles with the same ID='{data['key']}'")
        duplicated_ids.add(data['key'])

    # Now return only one example of duplicated profile, for further merging.
    # All duplicates will be loaded later.

    if duplicated_ids:
        for duplicated_profile_id in duplicated_ids:
            profile_record = await _load_by_id(duplicated_profile_id)
            yield profile_record.to_entity(Profile)


async def load_duplicated_profiles_by_field(field) -> AsyncGenerator[Tuple[str, int], Any]:
    result = await _get_duplicated_profiles_by_field(field)
    for bucket in result.aggregations('duplicate_emails').buckets():
        yield bucket['key'], bucket['doc_count']


async def load_profiles_by_field_and_value(field: str, email: str) -> AsyncGenerator[Profile, Any]:
    async for profile_record in _get_profiles_by_field_and_value(field, email):
        yield profile_record.to_entity(Profile)
