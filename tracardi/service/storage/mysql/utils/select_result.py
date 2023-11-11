from typing import Callable


class SelectResult:

    def __init__(self, result):
        self.result = result

    async def to_objects(self, mapper: Callable):
        for row in self.result:
            yield mapper(row)