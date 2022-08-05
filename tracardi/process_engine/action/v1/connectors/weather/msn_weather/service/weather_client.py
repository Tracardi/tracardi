import python_weather
from python_weather.response import Weather


class AsyncWeatherClient:

    METRIC = "C"
    IMPERIAL = "F"

    def __init__(self, type=None):
        if type is None:
            self.type = self.METRIC
        else:
            self.type = type

    async def fetch(self, city) -> Weather:
        client = python_weather.Client(format=self.type)
        weather = await client.find(city)
        await client.close()
        return weather
