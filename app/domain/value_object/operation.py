from typing import List

from pydantic import BaseModel


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
        return self.merge and isinstance(self.merge, list) and len(self.merge) > 0
