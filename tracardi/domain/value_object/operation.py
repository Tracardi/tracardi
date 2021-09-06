import tracardi
from typing import List
from pydantic import BaseModel
from tracardi.service.storage.factory import storage


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
    async def load_profiles_to_merge(merge_key_values: List[tuple], limit=1000) -> List['tracardi.domain.profile.Profile']:
        profiles = await storage('profile').load_by_values(merge_key_values, limit)
        return [tracardi.domain.profile.Profile(**profile) for profile in profiles]
