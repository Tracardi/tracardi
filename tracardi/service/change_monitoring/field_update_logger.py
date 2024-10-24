from typing import Optional, Any, Tuple, Set

from time import time


class FieldChanges(dict):

    def get_change(self, field:str):
        return self.get(field, [None, None])

    def exists(self, field: str) -> bool:
        return field in self

    def has_changes(self) -> bool:
        return bool(self)

class FieldUpdateLogger:

    def __init__(self):
        self._changes = FieldChanges()

    def _set(self, field, value, old_value):
        self._changes[field] = [time(), old_value]

    @staticmethod
    def _changed(value, old_value) -> bool:
        same = old_value != value
        if same:
            return True

        # Now check the lists
        if isinstance(old_value, list) and isinstance(value, list):
            return set(old_value) != set(value)

        return False

    def add(self,
            field,
            value,
            old_value,
            session_id: Optional[str] = None,
            event_type: Optional[str] = None,
            ignore: Tuple[str, ...] = None):

        if ignore and field.startswith(ignore):
            return

        if self._changed(value, old_value):
            self._set(field, value, old_value)

    def get(self, field, default):
        return self._changes.get(field, default)

    def timestamp(self, field) -> Optional[float]:
        field = self._changes.get(field, [None, None])
        return field[0]

    def changes(self):
        return self._changes.items()

    def has_changes(self) -> bool:
        return self._changes.has_changes()

    def get_logged_changes(self) -> FieldChanges:
        return  self._changes