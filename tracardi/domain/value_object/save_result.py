from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult


class SaveResult(BulkInsertResult):
    types: list = []

    def __add__(self, other):
        if not isinstance(other, SaveResult) and not isinstance(other, BulkInsertResult):
            raise ValueError("SaveResult can add only other SaveResult")

        self.saved += other.saved
        self.errors += other.errors
        self.ids += other.ids
        if isinstance(other, SaveResult):
            self.types += other.types

        return self

    def to_json(self):
        return {
            "saved": self.saved,
            "errors": self.errors,
            "ids": self.ids,
            "types": self.types
        }
