from json import JSONDecodeError
import aiohttp
import json
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.domain.resources.google_analytics_id import GoogleAnalyticsCredentials
from tracardi.service.storage.driver import storage
from tracardi.service.tracardi_http_client import HttpClient

from .model.configuration import Configuration


def validate(config: dict):
    return Configuration(**config)


class GoogleAnalyticsEventTrackerAction(ActionRunner):
    credentials: GoogleAnalyticsCredentials
    config: Configuration

    async def set_up(self, init):
        config = validate(init)
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=GoogleAnalyticsCredentials)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        url = 'https://www.google-analytics.com/collect'

        params = {
            "v": "1",
            "tid": self.credentials.google_analytics_id,
            "cid": self.profile.id,
            "t": "event",
            "ec": dot[self.config.category],
            "ea": dot[self.config.action],
            "el": dot[self.config.label],
            "ev": int(dot[self.config.value]),
        }

        async with HttpClient(self.node.on_connection_error_repeat) as client:
            async with client.post(
                    url=url,
                    data=params,
            ) as response:
                try:
                    content = await response.json(content_type=None)
                except JSONDecodeError:
                    content = await response.text()

                result = {
                    "status": response.status,
                    "content": content
                }
                if response.status in [200, 201, 202, 203]:
                    return Result(port="response", value=result)
                else:
                    return Result(port="error", value=result)
