import asyncio
import json
from datetime import datetime
import aiohttp
from tracardi.service.tracardi_http_client import HttpClient
from aiohttp import ClientConnectorError
from tracardi.config import tracardi
from tracardi.domain.resources.token import Token
from tracardi.service.domain import resource as resource_db
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.configuration import Configuration


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class AmplitudeSendEvent(ActionRunner):

    credentials: Token
    config: Configuration

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=Token)

    @staticmethod
    def _get_value(dot, dot_notation, allow_custom_value=False):

        if dot_notation is None:
            return None

        value = dot[dot_notation]
        if value == dot_notation:
            if allow_custom_value is True:
                return value
            return None
        return value

    async def run(self, payload: dict, in_edge=None) -> Result:

        try:

            dot = self._get_dot_accessor(payload)

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with HttpClient(
                self.node.on_connection_error_repeat,
                [200, 201, 202, 203],
                timeout=timeout
            ) as client:

                platform = self._get_value(dot, self.config.platform)
                properties = self._get_value(dot, self.config.event_properties)
                pii = self._get_value(dot, self.config.user_properties)
                event_type = self._get_value(dot, self.config.event_type)
                ip = self._get_value(dot, self.config.ip, allow_custom_value=True)

                event = {
                    "app_version": str(tracardi.version),
                    "insert_id": self.event.id if self.debug is False else None,
                    "user_id": self.profile.id,
                    "session_id": int(datetime.timestamp(
                        self.session.metadata.time.insert)) if self.profile.metadata.time.insert is not None else -1,
                    "event_type": self.event.type if event_type is None else event_type,
                    "event_properties": self.event.properties if not isinstance(properties, dict) else properties,
                    "user_properties": self.profile.data.pii.model_dump() if not isinstance(pii, dict) else pii,
                    "groups": self._get_value(dot, self.config.groups),
                    "ip": self.event.request['ip'] if 'ip' in self.event.request else ip,
                    "location_lat": self._get_value(dot, self.config.location_lat),
                    "location_lng": self._get_value(dot, self.config.location_lng),
                    "revenueType": self._get_value(dot, self.config.revenueType),
                    "productId": self._get_value(dot, self.config.productId),
                    "revenue": self._get_value(dot, self.config.revenue),
                    "quantity": self._get_value(dot, self.config.quantity),
                    "price": self._get_value(dot, self.config.price),
                    "language": self._get_value(dot, self.config.language),
                    "dma": self._get_value(dot, self.config.dma),
                    "city": self._get_value(dot, self.config.city),
                    "region": self._get_value(dot, self.config.region),
                    "country": self._get_value(dot, self.config.country),
                    "carrier": self._get_value(dot, self.config.carrier),
                    "device_model": self._get_value(dot, self.config.device_model),
                    "device_manufacturer": self._get_value(dot, self.config.device_manufacturer),
                    "device_brand": self._get_value(dot, self.config.device_brand),
                    "os_version": self._get_value(dot, self.config.os_version),
                    "os_name": self._get_value(dot, self.config.os_name),
                    "platform": self.session.context.get_platform() if platform is None else platform,
                }

                params = {
                    "api_key": self.credentials.token,
                    "events": [
                        event
                    ]
                }
                headers = {
                    'Content-Type': 'application/json',
                    'Accept': '*/*'
                }

                # print(params)

                async with client.post(
                        url=str(self.config.url),
                        headers=headers,
                        data=json.dumps(params)
                ) as response:

                    result = {
                        "status": response.status,
                        "content": await response.json()
                    }

                    if response.status in [200, 201, 202, 203]:
                        return Result(port="response", value=result)
                    else:
                        return Result(port="error", value=result)

        except ClientConnectorError as e:
            return Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="error", value="API timed out.")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='AmplitudeSendEvent',
            inputs=['payload'],
            outputs=["response", "error"],
            version="0.6.1",
            author="Risto Kowaczewski",
            license="Tracardi Pro",
            manual="amplitude_send_event"
        ),
        metadata=MetaData(
            name='Register event',
            brand='Amplitude',
            desc='Sends request to Amplitude API endpoint to register event.',
            icon='amplitude',
            group=["Amplitude"],
            tags=['analytics'],
            pro=True
        )
    )
