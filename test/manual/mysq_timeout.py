import asyncio

from tracardi.context import ServerContext, Context
from tracardi.service.cache.event_source import load_event_source_via_cache
from tracardi.service.decorators.function_memory_cache import async_cache_for


@async_cache_for(0, max_size=10, allow_null_values=False, lock=False, timeout=.001)
async def timeout():
    return await load_event_source_via_cache("ffaac23b-0266-40cb-9aef-b553d4954a52")


async def main():
    with ServerContext(Context(production=False)):
        print(await timeout())


asyncio.run(main())
