from typing import List

from pydantic import BaseModel

import tracardi.domain.profile

from tracardi.event_server.service.persistence_service import PersistenceService
from tracardi.service.storage.elastic_storage import ElasticStorage


class Operation(BaseModel):
    new: bool = False
    update: bool = False
    segment: bool = False
    merge: List[str] = []

    def needs_segmentation(self):
        return self.segment is True

    def needs_update(self):
        return self.update is True

    def needs_merging(self):
        return isinstance(self.merge, list) and len(self.merge) > 0

    @staticmethod
    async def load_profiles_to_merge(merge_key_values: List[tuple], limit=1000) -> List[
        'tracardi.domain.profile.Profile']:
        profiles = await PersistenceService(ElasticStorage('profile')).load_by_values(merge_key_values, limit)
        return [tracardi.domain.profile.Profile(**profile) for profile in profiles]
