from typing import Optional

from pydantic import BaseModel


class BulkInsertResult(BaseModel):
    saved: int = 0
    errors: list = []
    ids: list = []
    index: Optional[str] = None

    def __add__(self, other):
        if not isinstance(other, BulkInsertResult):
            raise ValueError("BulkInsertResult can add only other BulkInsertResult")

        self.saved += other.saved
        self.errors += other.errors
        self.ids += other.ids

        return self

    def is_nothing_saved(self) -> bool:
        return len(self.ids) == 0

    def has_errors(self) -> bool:
        return len(self.errors) > 0

    def number_of_errors(self) -> int:
        return len(self.errors)
