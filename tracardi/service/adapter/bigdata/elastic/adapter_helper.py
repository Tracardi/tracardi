from typing import Optional, Union, List, Set

from tracardi.domain.entity import FlatEntity
from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.session import Session
from tracardi.domain.storage_record import StorageRecord
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.adapter.bigdata.elastic.client.elastic_client import ElasticClient
from tracardi.service.adapter.bigdata.elastic.client.elastic_index import ElasticIndex

logger = get_logger(__name__)


def index(client: ElasticClient, idx) -> ElasticIndex:
    return ElasticIndex(client, idx)


async def _save_entities(client: ElasticClient, entities: Union[FlatEntity, List[FlatEntity], Set[FlatEntity]],
                         entity_index_type: str, **kwargs):
    entity_index = index(client, entity_index_type)
    result = await entity_index.save(entities, exclude={"operation": ...})
    if kwargs.get('refresh_after_save', False):
        await entity_index.flush()
    return result


async def load_profile(client: ElasticClient, profile_id: str, **kwargs) -> Optional[StorageRecord]:
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

    profile_records = await index(client, 'profile').query(query)
    if profile_records.total <= 0:
        return None

    if profile_records.total > 1:
        logger.warning(
            "Profile {} id duplicated in the database. It will be merged with APM worker.".format(profile_id))

    profile_record = profile_records.first()

    if profile_record is None:
        return None

    return profile_record


async def load_session(client: ElasticClient, session_id: str, **kwargs) -> Optional[StorageRecord]:
    session_record = await index(client, 'session').load(session_id)

    if session_record is None:
        return None

    return session_record


async def save_profiles(client: ElasticClient,
                        profiles: Union[FlatProfile, List[FlatProfile], Set[FlatProfile]],
                        **kwargs):
    return _save_entities(client, profiles, 'profile', **kwargs)


async def delete_profile(client: ElasticClient, id: str, idx: str):
    return await index(client, 'profile').delete(id, idx)


async def save_sessions(client: ElasticClient,
                        sessions: Union[Session, List[Session], Set[Session]],
                        **kwargs):
    return _save_entities(client, sessions, 'session', **kwargs)


async def save_events(client: ElasticClient,
                      events: Union[FlatEvent, List[FlatEvent], Set[FlatEvent]],
                      **kwargs):
    return _save_entities(client, events, 'event', **kwargs)
