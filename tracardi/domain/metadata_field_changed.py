from typing import Tuple, Optional, Any


class MetadataFieldChanged:

    def __init__(self, data: Optional[Tuple[float, Optional[Any]]]):
        self._data: Tuple[float, Optional[Any]] = data
        if self._data is None:
            self.timestamp = None
            self.old_value = None
        else:
            self.timestamp, self.old_value = self._data

    def is_older_then(self, timestamp: float) -> bool:
        return self.timestamp is None or timestamp >= self.timestamp

    def is_newer_then(self, timestamp: float) -> bool:
        return self.timestamp is None or timestamp <= self.timestamp

