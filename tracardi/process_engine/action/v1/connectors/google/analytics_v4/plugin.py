import json
from json import JSONDecodeError

from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from tracardi.service.tracardi_http_client import HttpClient
from .models.configuration import Configuration
from tracardi.domain.resources.google_analytics_v4 import GoogleAnalyticsV4Credentials


def validate(config: dict):
    return Configuration(**config)


class GoogleAnalyticsV4EventTrackerAction(ActionRunner):
    credentials: GoogleAnalyticsV4Credentials
    config: Configuration

    async def set_up(self, init):
        config = validate(init)
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=GoogleAnalyticsV4Credentials)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        url = f'https://www.google-analytics.com/mp/collect?measurement_id={self.credentials.measurement_id}' \
              f'&api_secret={self.credentials.api_key}'

        data = {
            "client_id": self.profile.id if self.profile.id else "unknown",
            "events": [{
                "name": dot[self.config.name],
                "params": dot[self.config.params]
            }]
        }
        async with HttpClient(self.node.on_connection_error_repeat) as client:
            body = json.dumps(data, separators=(',', ':'))
            print(body)
            async with client.post(
                    url=url,
                    data=body,
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
