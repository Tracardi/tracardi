import asyncio

from aiochclient import ChClient
from aiohttp import ClientSession


async def main():
    async with ClientSession() as s:
        client = ChClient(s, url='http://localhost:18123')
        print(await client.is_alive())

asyncio.run(main())