import aiohttp
from tracardi.service.tracardi_http_client import HttpClient as TracardiHttpClient


class HttpClient:
    def __init__(self, key, timeout=15, retries: int = 1):
        self.key = key
        self.timeout = timeout
        self.retries = retries

    async def send(self, string):
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with TracardiHttpClient(self.retries, 200, timeout=timeout) as client:
            params = {
                'key': self.key,
                'txt': string
            }
            async with client.request(
                    method="POST",
                    url=str("https://api.meaningcloud.com/lang-4.0/identification"),
                    data=params
            ) as response:
                result = {
                    "status": response.status,
                    "body": await response.json()
                }

                return response.status, result
