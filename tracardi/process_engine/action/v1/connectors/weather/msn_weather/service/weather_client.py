import python_weather
from aiohttp import ClientSession, ClientTimeout
from python_weather.forecast import Weather


class AsyncWeatherClient:

    METRIC = "C"
    IMPERIAL = "F"

    def __init__(self, type=None):
        if type is None:
            self.type = self.METRIC
        else:
            self.type = type

    async def fetch(self, city) -> Weather:
        client = python_weather.Client(format=self.type, session=ClientSession(timeout=ClientTimeout(total=5000.0)))
        weather = await client.get(city)
        await client.close()
        return weather
