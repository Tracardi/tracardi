from contextlib import asynccontextmanager

import asyncio


@asynccontextmanager
async def timeout(seconds):
    try:
        yield await asyncio.wait_for(asyncio.sleep(0), timeout=seconds)
    except asyncio.TimeoutError:
        print(f"Block timed out after {seconds} seconds")
        raise

