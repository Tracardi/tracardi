from typing import List, TypeVar, Union, Set
from adapter.bigdata.elastic.logging.logger import get_logger
from adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from tracardi.context import get_context
from tracardi.domain.session import Session
from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.tracking.cache.session_cache import save_session_cache
from .helpers.session_helper import load_by_id, get_nth_last_session, count_online, count_online_by_location, save, \
    save_sessions, delete_by_id, aggregate_session

T = TypeVar("T")

logger = get_logger(__name__)


class ElasticSessionAdapter(ElasticAdapter):

    async def load_session_from_db(self, session_id: str):
        return await load_by_id(session_id)

    async def load_nth_last_session_for_profile(self, profile_id: str, offset):
        return await get_nth_last_session(
            profile_id=profile_id,
            n=offset
        )

    async def count_sessions_online_in_db(self):
        return await count_online()

    async def count_online_sessions_by_location_in_db(self):
        result = await count_online_by_location()

        return {
            "events": result.total,
            "tz": [{"name": item['key'], "count": item['doc_count']} for item in result.aggregations("tz").buckets()]
        }

    # Standard

    async def count_sessions_in_db(self):
        return await self.core.count('session')

    async def refresh_session_db(self):
        await self.core.refresh('session')

    async def flush_session_db(self):
        await self.core.flush('session')

    async def save_session_to_db(self, session: Union[Session, List[Session], Set[Session]]):
        await save(session)

    async def save_session_to_db_and_cache(self, session: Union[Session, List[Session], Set[Session]]):
        context = get_context()
        save_session_cache(session, context)
        await self.save_session_to_db(session)

    async def save_sessions_in_db(self, sessions: List[Session]) -> BulkInsertResult:
        return await save_sessions(sessions)

    async def delete_session_from_db(self, session_id: str, index):
        return await delete_by_id(session_id, index=index)

    # Aggregates

    async def agg_sessions_by_app(self):
        bucket_name = 'sessions_by_app'
        result = await aggregate_session(bucket_name, by='app.name', buckets_size=20)

        if bucket_name not in result.aggregations:
            return []

        return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]

    async def agg_sessions_by_os_name(self):
        bucket_name = 'sessions_by_os_name'
        result = await aggregate_session(bucket_name, by='os.name', buckets_size=20)

        if bucket_name not in result.aggregations:
            return []

    async def agg_sessions_by_device_location(self):
        bucket_name = 'sessions_by_device_geo'
        result = await aggregate_session(bucket_name, by='device.geo.country.name', buckets_size=20)

        if bucket_name not in result.aggregations:
            return []

        return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]

    async def agg_sessions_by_channel(self):
        bucket_name = 'sessions_by_channel'
        result = await aggregate_session(bucket_name, by='metadata.channel', buckets_size=20)

        if bucket_name not in result.aggregations:
            return []

        return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]

    async def agg_sessions_by_resolution(self):
        bucket_name = 'sessions_by_resolution'
        result = await aggregate_session(bucket_name, by='device.resolution', buckets_size=20)

        if bucket_name not in result.aggregations:
            return []

        return [{"name": id, "value": count} for id, count in result.aggregations[bucket_name][0].items()]

