import asyncio
import json
from datetime import datetime

import aiohttp
from aiohttp import ClientConnectorError
from tracardi.config import tracardi
from tracardi.domain.resource import ResourceCredentials
from tracardi.domain.resources.token import Token
from tracardi.service.storage.driver import storage
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner
from .model.configuration import Configuration


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class AmplitudeSendEvent(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'AmplitudeSendEvent':
        config = validate(kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return AmplitudeSendEvent(config, resource.credentials)

    def __init__(self, config, credentials: ResourceCredentials):
        self.config = config  # type: Configuration
        self.credentials = credentials.get_credentials(self, output=Token)

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

    async def run(self, payload):

        try:

            dot = self._get_dot_accessor(payload)

            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            async with aiohttp.ClientSession(timeout=timeout) as session:

                platform = self._get_value(dot, self.config.platform)
                properties = self._get_value(dot, self.config.event_properties)
                pii = self._get_value(dot, self.config.user_properties)
                event_type = self._get_value(dot, self.config.event_type)
                ip = self._get_value(dot, self.config.ip, allow_custom_value=True)

                event = {
                    "app_version": tracardi.version,
                    "insert_id": self.event.id if self.debug is False else None,
                    "user_id": self.profile.id,
                    "session_id": int(datetime.timestamp(self.session.metadata.time.insert)) if self.profile.metadata.time.insert is not None else -1,
                    "event_type": self.event.type if event_type is None else event_type,
                    "event_properties": self.event.properties if not isinstance(properties, dict) else properties,
                    "user_properties": self.profile.pii.dict() if not isinstance(pii, dict) else pii,
                    "groups": self._get_value(dot, "groups"),
                    "ip": self.event.metadata.ip if ip is None else ip,
                    "location_lat": self._get_value(dot, "location_lat"),
                    "location_lng": self._get_value(dot, "location_lng"),
                    "revenueType": self._get_value(dot, "revenueType"),
                    "productId": self._get_value(dot, "productId"),
                    "revenue": self._get_value(dot, "revenue"),
                    "quantity": self._get_value(dot, "quantity"),
                    "price": self._get_value(dot, "price"),
                    "language": self._get_value(dot, "language"),
                    "dma": self._get_value(dot, "dma"),
                    "city": self._get_value(dot, "city"),
                    "region": self._get_value(dot, "region"),
                    "country": self._get_value(dot, "country"),
                    "carrier": self._get_value(dot, "carrier"),
                    "device_model": self._get_value(dot, "device_model"),
                    "device_manufacturer": self._get_value(dot, "device_manufacturer"),
                    "device_brand": self._get_value(dot, "device_brand"),
                    "os_version": self._get_value(dot, "os_version"),
                    "os_name": self._get_value(dot, "os_name"),
                    "platform": self.session.get_platform() if platform is None else platform,
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

                async with session.post(
                        url=str(self.config.url),
                        headers=headers,
                        data=json.dumps(params)
                ) as response:

                    result = {
                        "status": response.status,
                        "content": await response.json()
                    }

                    if response.status in [200, 201, 202, 203]:
                        return Result(port="response", value=result), Result(port="error", value=None)
                    else:
                        return Result(port="response", value=None), Result(port="error", value=result)

        except ClientConnectorError as e:
            return Result(port="response", value=None), Result(port="error", value=str(e))

        except asyncio.exceptions.TimeoutError:
            return Result(port="response", value=None), Result(port="error", value="API timed out.")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='AmplitudeSendEvent',
            inputs=['payload'],
            outputs=["response", "error"],
            init={
                "source": {"id": None},
                "url": "https://api2.amplitude.com/2/httpapi",
                "timeout": 15,
                "event_type": None,
                "event_properties": None,
                "user_properties": None,
                "groups": None,
                "ip": None,
                "location_lat": None,
                "location_lng": None,
                "revenueType": None,
                "productId": None,
                "revenue": None,
                "quantity": None,
                "price": None,
                "language": None,
                "dma": None,
                "city": None,
                "region": None,
                "country": None,
                "carrier": None,
                "device_model": None,
                "device_manufacturer": None,
                "device_brand": None,
                "os_version": None,
                "os_name": None,
                "platform": None,
            },
            form=Form(groups=[
                FormGroup(
                    name="Amplitude source",
                    fields=[
                        FormField(
                            id="source",
                            name="Amplitude resource",
                            description="Please select your Amplitude resource.",
                            component=FormComponent(type="resource", props={"label": "Resource", "tag": "token"})
                        ),
                    ]),
                FormGroup(
                    name="Amplitude Api Configuration",
                    fields=[
                        FormField(
                            id="url",
                            name="API URL",
                            description="Please type API URL if it is different then default Amplitude URL.",
                            component=FormComponent(type="text", props={"label": "API URL"})
                        ),
                        FormField(
                            id="timeout",
                            name="API timeout",
                            description="Please API timeout.",
                            component=FormComponent(type="text", props={"label": "API timeout"})
                        ),
                    ]),
                FormGroup(
                    name="Amplitude Event Configuration",
                    description="Select what data should be sent to Amplitude. Leave empty if you want to send "
                                "default data.",
                    fields=[
                        FormField(
                            id="event_type",
                            name="Event type",
                            description="Leave empty if the current event type is to be copied.",
                            component=FormComponent(type="dotPath", props={"label": "Path to event type"})
                        ),
                        FormField(
                            id="event_properties",
                            name="Event properties",
                            description="Leave empty if the current event properties is to be copied.",
                            component=FormComponent(type="dotPath", props={"label": "Path to event properties"})
                        ),
                        FormField(
                            id="user_properties",
                            name="User PII",
                            description="Leave empty if the current profile PII is to be copied.",
                            component=FormComponent(type="dotPath", props={"label": "Path to profile PII"})
                        ),
                        FormField(
                            id="ip",
                            name="IP address",
                            description="Leave empty if the events ip to be copied.",
                            component=FormComponent(type="dotPath", props={"label": "IP address"})
                        ),
                    ])
            ]),
            version="0.6.1",
            author="Risto Kowaczewski",
            license="MIT",
            manual="amplitude_send_event"
        ),
        metadata=MetaData(
            name='Amplitude register event',
            desc='Sends request to Amplitude API endpoint to register event.',
            icon='bar-chart',
            group=["Connectors", "Stats"]
        )
    )
