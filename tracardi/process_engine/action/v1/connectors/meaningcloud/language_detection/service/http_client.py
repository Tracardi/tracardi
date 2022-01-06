import aiohttp


class HttpClient:
    def __init__(self, key, timeout=15):
        self.key = key
        self.timeout = timeout

    async def send(self, string):
        timeout = aiohttp.ClientTimeout(total=self.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:
            params = {
                'key': self.key,
                'txt': string
            }
            async with session.request(
                    method="POST",
                    url=str("https://api.meaningcloud.com/lang-4.0/identification"),
                    data=params
            ) as response:
                result = {
                    "status": response.status,
                    "body": await response.json()
                }

                return response.status, result
