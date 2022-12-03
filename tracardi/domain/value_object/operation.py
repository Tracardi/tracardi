from typing import List
from pydantic import BaseModel


class RecordFlag(BaseModel):
    new: bool = False
    update: bool = False

    def needs_update(self):
        return self.update is True


class Operation(RecordFlag):
    segment: bool = False
    merge: List[str] = []

    def needs_segmentation(self):
        return self.segment is True

    def needs_merging(self):
        return isinstance(self.merge, list) and len(self.merge) > 0
