from pydantic import BaseModel


class Operation(BaseModel):
    new: bool = False
    update: bool = False
    segment: bool = False
    merge: bool = False

    def needs_segmentation(self):
        return self.update or self.segment

    def needs_update(self):
        return self.update or self.merge
