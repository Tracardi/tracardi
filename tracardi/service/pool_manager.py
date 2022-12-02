import asyncio
from collections import defaultdict
from typing import List, Dict


class PoolManager:

    def __init__(self, name, max_pool, on_pool_purge=None,
                 on_append=None,
                 pass_pool_as_dict=False,
                 replace_item_on_append=False,
                 wait_for_pool_purge_finish=True
                 ):
        self.name = name
        self.replace_item_on_append = replace_item_on_append
        self.on_append = on_append
        self.max_pool = max_pool
        self.on_pool_purge = on_pool_purge
        self.items: Dict[str, List] = defaultdict(list)
        self.counter = 0
        self.ttl = 0
        self.loop = None
        self.last_task = None
        self.pass_pool_as_dict = pass_pool_as_dict
        self.attributes = None
        self.wait_for_pool_purge_finish = wait_for_pool_purge_finish

    def set_attributes(self, attributes):
        self.attributes = attributes

    def set_ttl(self, loop, ttl):
        self.ttl = ttl
        self.loop = loop

    async def _invoke(self, items):
        if self.on_pool_purge:
            if self.pass_pool_as_dict:
                pool_payload = items
            else:
                pool_payload = items[self.name]

            result = self.on_pool_purge(pool_payload, self.attributes)
            if asyncio.iscoroutinefunction(self.on_pool_purge):
                await result

    async def _append(self, item):
        if self.on_append:
            result = self.on_append(item, self.attributes)
            if asyncio.iscoroutinefunction(self.on_append):
                result = await result
            return result

    def __await__(self):
        async def closure():
            return self

        return closure().__await__()

    async def __aenter__(self):
        return self

    def purge_task(self):
        asyncio.create_task(self.purge())

    async def _purge(self, items):
        if self.last_task:
            self.last_task.cancel()
        await self._invoke(items)

    async def purge(self):
        await self._purge(dict(self.items))

    async def __aexit__(self, exc_type, exc_value, exc_traceback):
        await self.purge()

    async def append(self, item, key=None):
        if self.on_append:
            result = await self._append(item)
            if self.replace_item_on_append:
                item = result
        key = key if key else self.name
        self.items[key].append(item)
        self.counter += 1
        print('counter', self.counter, self.max_pool)

        if self.counter >= self.max_pool:
            # Make sure that we have a copy of items to process
            items = dict(self.items)
            # Now reset
            self.counter = 0
            self.items = defaultdict(list)
            await self._purge(items)

        elif self.ttl > 0 and self.loop:
            print('call for later')
            if self.last_task:
                self.last_task.cancel()
            self.last_task = self.loop.call_later(self.ttl, self.purge_task)
