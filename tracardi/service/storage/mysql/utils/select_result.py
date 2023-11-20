from typing import Callable


class SelectResult:

    def __init__(self, result):
        self.result = result

    def to_objects(self, mapper: Callable):
        for row in self.result:
            yield mapper(row)

    def get_object(self, mapper):
        return mapper(self.result)

    def exists(self) -> bool:
        return self.result is not None