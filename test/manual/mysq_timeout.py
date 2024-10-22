import asyncio

from tracardi.context import ServerContext, Context
from tracardi.service.cache.event_source import load_event_source_via_cache
from tracardi.service.decorators.async_cache import AsyncCache


@AsyncCache(0, allow_null_values=False, lock=False, timeout=.001)
async def timeout():
    return await load_event_source_via_cache("ffaac23b-0266-40cb-9aef-b553d4954a52")


async def main():
    with ServerContext(Context(production=False)):
        print(await timeout())


asyncio.run(main())
