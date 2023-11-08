from typing import Type


class SelectResult:

    def __init__(self, result):
        self.result = result

    async def to_objects(self, mapper: Type):
        for row in await self.result:
            yield mapper(row)