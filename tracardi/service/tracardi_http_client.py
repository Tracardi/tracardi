import aiohttp
from typing import Union, Tuple, Callable, List
from contextlib import asynccontextmanager


class HttpClient:

    def __init__(self, retries: int = 1, accept_status: Union[int, Tuple[int], List[int]] = 200, *args, **kwargs):
        self.client = aiohttp.ClientSession(*args, **kwargs)
        self.retries = retries if retries >= 1 else 1
        self.accept_status = tuple([accept_status]) if isinstance(accept_status, int) else accept_status

    async def _run_with_retries(self, func: Callable, *args, **kwargs):
        for retry in range(self.retries):
            response = await func(*args, **kwargs)
            if response.status in self.accept_status or retry == self.retries - 1:
                return response

    @asynccontextmanager
    async def request(self, *args, **kwargs):
        yield await self._run_with_retries(self.client.request, *args, **kwargs)

    @asynccontextmanager
    async def get(self, *args, **kwargs):
        yield await self._run_with_retries(self.client.get, *args, **kwargs)

    @asynccontextmanager
    async def put(self, *args, **kwargs):
        yield await self._run_with_retries(self.client.put, *args, **kwargs)

    @asynccontextmanager
    async def post(self, *args, **kwargs):
        yield await self._run_with_retries(self.client.post, *args, **kwargs)

    @asynccontextmanager
    async def delete(self, *args, **kwargs):
        yield await self._run_with_retries(self.client.delete, *args, **kwargs)

    @asynccontextmanager
    async def patch(self, *args, **kwargs):
        yield await self._run_with_retries(self.client.patch, *args, **kwargs)

    async def __aenter__(self) -> 'HttpClient':
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb) -> None:
        await self.client.close()
