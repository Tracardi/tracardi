from typing import Optional, Union, List, Set

from tracardi.domain.flat_event import FlatEvent
from tracardi.domain.flat_profile import FlatProfile
from tracardi.domain.session import Session
from tracardi.common.logging.log_handler import get_logger
from adapter.bigdata.elastic.elastic_adapter import ElasticAdapter
from adapter.bigdata.elastic.helpers.adapter_helper import (load_profile as load_profile_helper)

logger = get_logger(__name__)


class ElasticCollectorAdapter(ElasticAdapter):

    async def load_session(self, session_id: str, **kwargs) -> Optional[Session]:
        session_record = await self.core.load('session', session_id, **kwargs)

        if session_record is None:
            return None

        session = session_record.to_entity(Session)

        return session

    async def load_profile(self, profile_id: str, **kwargs) -> Optional[FlatProfile]:
        profile_record = await load_profile_helper(self._client, profile_id, **kwargs)

        if profile_record is None:
            return None

        return FlatProfile.from_es_storage_record(profile_record)

    async def save_profiles(self, profiles: Union[FlatProfile, List[FlatProfile], Set[FlatProfile]], **kwargs):
        return await self.core.save('profile', profiles, **kwargs)

    async def save_sessions(self, sessions: Union[Session, List[Session], Set[Session]], **kwargs):
        return await self.core.save('session', sessions, **kwargs)

    async def save_events(self, events: Union[FlatEvent, List[FlatEvent], Set[FlatEvent]], **kwargs):
        return await self.core.save('event', events, **kwargs)
