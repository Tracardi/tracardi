from pydantic import BaseModel


class BulkInsertResult(BaseModel):
    saved: int = 0
    errors: list = []
    ids: list = []

    def __add__(self, other):
        if not isinstance(other, BulkInsertResult):
            raise ValueError("BulkInsertResult can add only other BulkInsertResult")

        self.saved += other.saved
        self.errors += other.errors
        self.ids += other.ids

        return self

    def is_nothing_saved(self) -> bool:
        return len(self.ids) == 0
