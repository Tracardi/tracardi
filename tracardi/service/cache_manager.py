from typing import Optional, List, Generator

from tracardi.domain.destination import Destination
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.domain.event_source import EventSource
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.domain.event_validator import EventValidator
from tracardi.domain.session import Session
from tracardi.domain.storage_record import StorageRecords
from tracardi.event_server.utils.memory_cache import MemoryCache
from tracardi.service.singleton import Singleton
from tracardi.service.storage.driver.elastic import session as session_db
from tracardi.service.storage.driver.elastic import event_to_profile as event_to_profile_db
from tracardi.service.storage.driver.elastic import data_compliance as data_compliance_db
from tracardi.service.storage.mysql.mapping.destination_mapping import map_to_destination
from tracardi.service.storage.mysql.mapping.event_reshaping_mapping import map_to_event_reshaping
from tracardi.service.storage.mysql.mapping.event_source_mapping import map_to_event_source
from tracardi.service.storage.mysql.mapping.event_to_event_mapping import map_to_event_mapping
from tracardi.service.storage.mysql.mapping.event_to_profile_mapping import map_to_event_to_profile
from tracardi.service.storage.mysql.mapping.event_validation_mapping import map_to_event_validation
from tracardi.service.storage.mysql.service.destination_service import DestinationService
from tracardi.service.storage.mysql.service.event_mapping_service import EventMappingService
from tracardi.service.storage.mysql.service.event_reshaping_service import EventReshapingService
from tracardi.service.storage.mysql.service.event_source_service import EventSourceService
from tracardi.service.storage.mysql.service.event_to_profile_service import EventToProfileMappingService
from tracardi.service.storage.mysql.service.event_validation_service import EventValidationService


class CacheManager(metaclass=Singleton):
    _cache = {
        'SESSION': MemoryCache("session", max_pool=1000, allow_null_values=False),
        'EVENT_SOURCE': MemoryCache("event-source", max_pool=100, allow_null_values=False),
        'EVENT_VALIDATION': MemoryCache("event-validation", max_pool=500, allow_null_values=True),
        'EVENT_TAG': MemoryCache("event-tags", max_pool=200, allow_null_values=True),
        'EVENT_RESHAPING': MemoryCache("event-reshaping", max_pool=200, allow_null_values=True),
        'EVENT_INDEXING': MemoryCache("event-indexing", max_pool=200, allow_null_values=True),
        'EVENT_TO_PROFILE_COPING': MemoryCache("event-to-profile-coping", max_pool=200, allow_null_values=True),
        'EVENT_DESTINATION': MemoryCache("event-destinations", max_pool=100, allow_null_values=True),
        'PROFILE_DESTINATIONS': MemoryCache("profile-destinations", max_pool=10, allow_null_values=True),
        'EVENT_CONSENT_COMPLIANCE': MemoryCache("event-consent-compliance", max_pool=500, allow_null_values=True),
    }

    def session_cache(self) -> MemoryCache:
        return self._cache['SESSION']

    def event_source_cache(self) -> MemoryCache:
        return self._cache['EVENT_SOURCE']

    def event_validation_cache(self) -> MemoryCache:
        return self._cache['EVENT_VALIDATION']

    def event_metadata_cache(self) -> MemoryCache:
        return self._cache['EVENT_TAG']

    def event_reshaping_cache(self) -> MemoryCache:
        return self._cache['EVENT_RESHAPING']

    def event_indexing_cache(self) -> MemoryCache:
        return self._cache['EVENT_INDEXING']

    def event_to_profile_coping_cache(self) -> MemoryCache:
        return self._cache['EVENT_TO_PROFILE_COPING']

    def profile_destination_cache(self) -> MemoryCache:
        return self._cache['PROFILE_DESTINATIONS']

    def event_destination_cache(self) -> MemoryCache:
        return self._cache['EVENT_DESTINATION']

    def event_consent_compliance_cache(self) -> MemoryCache:
        return self._cache['EVENT_CONSENT_COMPLIANCE']

    # Caches

    async def event_destination(self, event_type, source_id, ttl) -> List[Destination]:
        """
        Session cache
        """

        async def _load_event_destinations(event_type, source_id) -> List[Destination]:
            ds = DestinationService()
            return (await ds.load_event_destinations(event_type, source_id)).map_to_objects(map_to_destination)


        if ttl > 0:
            return await MemoryCache.cache(
                self.event_destination_cache(),
                f"{event_type}-{source_id}",
                ttl,
                _load_event_destinations,
                True,
                event_type,
                source_id
            )

        return await _load_event_destinations(event_type, source_id)

    async def profile_destinations(self, ttl) -> List[Destination]:
        """
        Session cache
        """

        async def _load_profile_destinations() -> List[Destination]:
            ds = DestinationService()
            return (await ds.load_profile_destinations()).map_to_objects(map_to_destination)

        if ttl > 0:
            return await MemoryCache.cache(
                self.profile_destination_cache(),
                "profile-destination-key",
                ttl,
                _load_profile_destinations,
                True
            )

        return await _load_profile_destinations()

    async def session(self, session_id, ttl) -> Optional[Session]:
        """
        Session cache
        """
        if ttl > 0:
            return await MemoryCache.cache(
                self.session_cache(),
                session_id,
                ttl,
                session_db.load_by_id,
                True,
                session_id
            )

        return await session_db.load_by_id(session_id)

    async def save_session(self, session: Session, ttl):
        await MemoryCache.save(
            self.session_cache(),
            session.id,
            session.model_dump(),
            ttl
        )

    async def event_source(self, event_source_id, ttl) -> Optional[EventSource]:
        """
        Event source cache
        """

        async def _load_event_source(source_id) -> Optional[EventSource]:
            ess = EventSourceService()
            return (await ess.load_by_id(source_id)).map_to_object(map_to_event_source)

        if ttl > 0:
            return await MemoryCache.cache(
                self.event_source_cache(),
                event_source_id,
                ttl,
                _load_event_source,
                True,
                event_source_id
            )


        return await _load_event_source(event_source_id)

    async def event_validation(self, event_type, ttl) -> List[EventValidator]:
        """
        Event validation schema cache
        """

        async def _load_event_validation(event_type: str) -> List[EventValidator]:
            evs = EventValidationService()
            return list((await evs.load_by_event_type(event_type, only_enabled=True)).map_to_objects(map_to_event_validation))

        if ttl > 0:
            return await MemoryCache.cache(
                self.event_validation_cache(),
                event_type,
                ttl,
                _load_event_validation,
                True,
                event_type)

        return await _load_event_validation(event_type)

    async def event_consent_compliance(self, event_type, ttl) -> StorageRecords:
        """
        Event consent compliance
        """
        if ttl > 0:
            return await MemoryCache.cache(
                self.event_consent_compliance_cache(),
                event_type,
                ttl,
                data_compliance_db.load_by_event_type,
                True,
                event_type)
        return await data_compliance_db.load_by_event_type(event_type)

    async def event_to_profile_coping(self, event_type, ttl) -> List[EventToProfile]:
        """
        Event to profile coping schema cache
        """

        async def _load_event_to_profile(event_type_id: str) -> List[EventToProfile]:
            etpms = EventToProfileMappingService()
            records = await etpms.load_by_type(event_type_id, enabled_only=True)
            if not records.exists():
                return []
            return list(records.map_to_objects(map_to_event_to_profile))

        if ttl > 0:
            return await MemoryCache.cache(
                self.event_to_profile_coping_cache(),
                event_type,
                ttl,
                _load_event_to_profile,
                True,
                event_type,
                True  # Only enabled
            )
        return await _load_event_to_profile(event_type)

    async def event_mapping(self, event_type_id, ttl) -> Optional[EventTypeMetadata]:

        async def _load_event_mapping(event_type_id: str) -> Optional[EventTypeMetadata]:
            ems = EventMappingService()
            record = await ems.load_by_event_type_id(event_type_id, only_enabled=True)
            if not record.exists():
                return None
            return record.map_to_object(map_to_event_mapping)

        if ttl > 0:
            return await MemoryCache.cache(
                self.event_metadata_cache(),
                event_type_id,
                ttl,
                _load_event_mapping,
                True,
                event_type_id)

        return await _load_event_mapping(event_type_id)

    @staticmethod
    async def _load_and_convert_reshaping(event_type) -> Optional[List[EventReshapingSchema]]:
        ers = EventReshapingService()
        reshape_schemas = await ers.load_by_event_type(event_type)
        if reshape_schemas.exists():
            return reshape_schemas.map_to_objects(map_to_event_reshaping)
        return None

    async def event_reshaping(self, event_type, ttl) -> Optional[List[EventReshapingSchema]]:
        if ttl > 0:
            return await MemoryCache.cache(
                self.event_reshaping_cache(),
                event_type,
                ttl,
                self._load_and_convert_reshaping,
                True,
                event_type)
        return await self._load_and_convert_reshaping(event_type)
