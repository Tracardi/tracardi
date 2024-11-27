import asyncio
from typing import Union, List, Set, Tuple, AsyncGenerator, Any

from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.profile import Profile
from tracardi.domain.storage_record import RecordMetadata, StorageRecords
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.service.adapter.bigdata.elastic.helpers.adapter_helper import (load_profile as load_profile_helper)
from tracardi.service.adapter.bigdata.elastic.client.elastic_query import get_query_by_values, \
    get_query_for_duplicated_profiles_by_ids, get_query_for_auto_merge, get_agg_query_for_duplicated_profile_counts, \
    get_update_query_to_update_profile_id, get_agg_query_for_duplicated_profiles_by_field, \
    get_query_to_load_by_field_and_value

logger = get_logger(__name__)

class ElasticApmAdapter(ElasticAdapter):

    async def load_duplicated_profiles_by_field(self, field: str) -> AsyncGenerator[Tuple[str, int], None]:
        query = get_agg_query_for_duplicated_profiles_by_field(field)
        result = await self.index('profile').query(query)
        for bucket in result.aggregations('duplicate_emails').buckets():
            yield bucket['key'], bucket['doc_count']

    async def load_profiles_by_field_and_value(self, field: str, value: str) -> AsyncGenerator[FlatProfile, Any]:
        query = get_query_to_load_by_field_and_value(field, value)
        async for profile_record in self.index('profile').scan(query, batch=1000):
            yield FlatProfile.from_es_storage_record(profile_record)

    async def load_profiles_with_duplicated_ids(self) -> AsyncGenerator[Profile, Any]:

        query = get_agg_query_for_duplicated_profile_counts()
        records = await self.index('profile').query(query)

        duplicated_ids = set()
        for data in records.aggregations("duplicate_ids").buckets():
            logger.info(f"Found {data['doc_count']} profiles with the same ID='{data['key']}'")
            duplicated_ids.add(data['key'])

        # Now return only one example of duplicated profile, for further merging.
        # All duplicates will be loaded later.

        if duplicated_ids:
            for duplicated_profile_id in duplicated_ids:
                profile_record = await load_profile_helper(self._client, duplicated_profile_id)
                yield profile_record.to_entity(Profile)

    async def load_profiles_marked_for_auto_merge(self) -> AsyncGenerator[Profile, Any]:
        query = get_query_for_auto_merge()
        async for profile_record in self.index('profile').scan(query, batch=1000):
            yield profile_record.to_entity(Profile)

    async def load_duplicated_profiles_with_ids(self, profile_ids: Set[str]) -> StorageRecords:
        query = get_query_for_duplicated_profiles_by_ids(list(profile_ids))
        return await self.index('profile').query(query)

    async def load_duplicated_profiles_with_merge_key(self, merge_by: List[Tuple[str, str]], condition='must',
                                                      limit=1000) -> StorageRecords:
        query = get_query_by_values(
            merge_by,
            condition=condition,
            limit=limit)
        return await self.index('profile').query(query)

    # Mutations

    async def save_profiles(self, profiles: Union[FlatProfile, List[FlatProfile], Set[FlatProfile]], **kwargs):
        return await self.core.save('profile', profiles, **kwargs)

    async def delete_multiple_profiles(self, profile_tuples: List[Tuple[str, RecordMetadata]]):
        tasks = [asyncio.create_task(self.core.delete('profile', profile_id, metadata.index))
                 for profile_id, metadata in profile_tuples]
        return await asyncio.gather(*tasks)

    async def update_profile_id_in(self, index: str, old_profile_id: str, merged_profile_id):
        query = get_update_query_to_update_profile_id(old_profile_id, new_profile_id=merged_profile_id)
        return await self.core.update(index, query=query)

    async def move_profile_events_and_sessions(self, duplicate_profile_ids: Set[str], merged_profile_id: str):
        # Changes ids of old events and sessions to match merged profile
        for old_id in duplicate_profile_ids:
            if old_id != merged_profile_id:
                await self.update_profile_id_in('event', old_id, merged_profile_id)
                await self.core.refresh('event')
                await self.update_profile_id_in('session', old_id, merged_profile_id)
                await self.core.refresh('session')
