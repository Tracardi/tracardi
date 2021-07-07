from typing import List

from pydantic import BaseModel

import app.domain.profile

from app.event_server.service.persistence_service import PersistenceService
from app.service.storage.elastic_storage import ElasticStorage


class Operation(BaseModel):
    new: bool = False
    update: bool = False
    segment: bool = False
    merge: List[str] = []

    def needs_segmentation(self):
        return self.update or self.segment

    def needs_update(self):
        return self.update or self.merge

    def needs_merging(self):
        return isinstance(self.merge, list) and len(self.merge) > 0

    @staticmethod
    async def get_merge_profiles(merge_key_values: List[tuple]) -> List['app.domain.profile.Profile']:
        profiles = await PersistenceService(ElasticStorage('profile')).load_by_values(merge_key_values)
        return [app.domain.profile.Profile(**profile) for profile in profiles]
