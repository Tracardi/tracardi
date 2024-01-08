import asyncio
from collections import defaultdict
from typing import List, Dict, Callable, Any, Union, Tuple


class PoolManager:

    def __init__(self,
                 name,
                 max_pool,
                 on_pool_purge: Callable[[Union[Dict, List], Tuple], Any] = None,
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
            pool_payload = None

            if self.pass_pool_as_dict:
                pool_payload = items
            else:
                if self.name in items:
                    pool_payload = items[self.name]

            if not pool_payload:
                return

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

    async def __invoke_purge_callable(self, items):
        if self.last_task:
            self.last_task.cancel()
        await self._invoke(items)

    async def _purge(self, items):
        await self.__invoke_purge_callable(items)
        self.items = defaultdict(list)
        self.counter = 0

    def _purge_task(self):
        items = dict(self.items)
        # Reset first then invoke
        self.counter = 0
        self.items = defaultdict(list)
        asyncio.create_task(self.__invoke_purge_callable(items))

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

        if self.counter >= self.max_pool:
            # Make sure that we have a copy of items to process
            items = dict(self.items)
            # Now reset
            await self._purge(items)

        elif self.ttl > 0 and self.loop:
            if self.last_task:
                self.last_task.cancel()
            self.last_task = self.loop.call_later(self.ttl, self._purge_task)
