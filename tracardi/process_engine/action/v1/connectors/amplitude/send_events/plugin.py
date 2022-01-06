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
                    "session_id": int(datetime.timestamp(
                        self.session.metadata.time.insert)) if self.profile.metadata.time.insert is not None else -1,
                    "event_type": self.event.type if event_type is None else event_type,
                    "event_properties": self.event.properties if not isinstance(properties, dict) else properties,
                    "user_properties": self.profile.pii.dict() if not isinstance(pii, dict) else pii,
                    "groups": self._get_value(dot, self.config.groups),
                    "ip": self.event.metadata.ip if ip is None else ip,
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
                "language": None,
                "dma": None,
                "city": None,
                "region": None,
                "country": None,

                "revenueType": None,
                "productId": None,
                "revenue": None,
                "quantity": None,
                "price": None,

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
                            name="User Personal Identifiable Information (PII)",
                            description="Leave empty if the current profile PII is to be copied.",
                            component=FormComponent(type="dotPath", props={"label": "Path to profile PII"})
                        ),
                        FormField(
                            id="groups",
                            name="Groups",
                            description="Group types are only available to Growth and Enterprise customers who have "
                                        "purchased the Accounts add-on on Amplitude.",
                            component=FormComponent(type="dotPath", props={"label": "IP Groups"})
                        ),
                    ]),
                FormGroup(
                    name="Amplitude Location Configuration",
                    description="Select what data should be sent to Amplitude. Leave empty if you want to send "
                                "default data.",
                    fields=[
                        FormField(
                            id="ip",
                            name="IP address",
                            description="Leave empty if the events ip to be copied.",
                            component=FormComponent(type="dotPath", props={"label": "IP address"})
                        ),
                        FormField(
                            id="location_lat",
                            name="Latitude",
                            description="Leave empty if you want Amplitude to read location from IP.",
                            component=FormComponent(type="dotPath", props={"label": "Path to latitude"})
                        ),
                        FormField(
                            id="location_lng",
                            name="Longitude",
                            description="Leave empty if you want Amplitude to read location from IP.",
                            component=FormComponent(type="dotPath", props={"label": "Path to longitude"})
                        ),
                        FormField(
                            id="language",
                            name="Language",
                            description="The language set by the user.",
                            component=FormComponent(type="dotPath", props={"label": "Path to Language"})
                        ),
                        FormField(
                            id="dma",
                            name="Designated Market Area (DMA)",
                            description="The current Designated Market Area of the user.",
                            component=FormComponent(type="dotPath", props={"label": "Path to DMA"})
                        ),
                        FormField(
                            id="city",
                            name="City",
                            description="The current city of the user.",
                            component=FormComponent(type="dotPath", props={"label": "Path to city"})
                        ),
                        FormField(
                            id="region",
                            name="Region",
                            description="The current region of the user.",
                            component=FormComponent(type="dotPath", props={"label": "Path to region"})
                        ),
                        FormField(
                            id="country",
                            name="Country",
                            description="The current country of the user.",
                            component=FormComponent(type="dotPath", props={"label": "Path to country"})
                        ),
                    ]),
                FormGroup(
                    name="Amplitude Product Configuration",
                    description="Select what data should be sent to Amplitude. Leave empty if you want to send "
                                "default data.",
                    fields=[

                        FormField(
                            id="productId",
                            name="Product ID",
                            description="An identifier for the item purchased. You must send a price and quantity "
                                        "or revenue with this field.",
                            component=FormComponent(type="dotPath", props={"label": "Path to productId"})
                        ),
                        FormField(
                            id="revenue",
                            name="Revenue",
                            description="revenue = price * quantity. If you send all 3 fields of price, quantity, and "
                                        "revenue, then (price * quantity) will be used as the revenue value. You can "
                                        "use negative values to indicate refunds.",
                            component=FormComponent(type="dotPath", props={"label": "Path to revenue"})
                        ),
                        FormField(
                            id="revenueType",
                            name="Revenue type",
                            description="The type of revenue for the item purchased. You must send a price and "
                                        "quantity or revenue with this field.",
                            component=FormComponent(type="dotPath", props={"label": "Path to revenue type",
                                                                           "defaultMode": 2})
                        ),
                        FormField(
                            id="quantity",
                            name="Quantity",
                            description="The quantity of the item purchased. Defaults to 1 if not specified.",
                            component=FormComponent(type="dotPath", props={"label": "Path to quantity"})
                        ),
                        FormField(
                            id="price",
                            name="Price",
                            description="The price of the item purchased. Required for revenue data if the revenue "
                                        "field is not sent. You can use negative values to indicate refunds.",
                            component=FormComponent(type="dotPath", props={"label": "Path to price"})
                        ),
                    ]),
                FormGroup(
                    name="Amplitude Device Configuration",
                    description="Select what data should be sent to Amplitude. Leave empty if you want to send "
                                "default data.",
                    fields=[
                        FormField(
                            id="platform",
                            name="Platform",
                            description="Platform of the device.",
                            component=FormComponent(type="dotPath", props={"label": "Path to platform"})
                        ),
                        FormField(
                            id="os_name",
                            name="Operation System Name (OS)",
                            description="The name of the mobile operating system or browser that the user is using.",
                            component=FormComponent(type="dotPath", props={"label": "Path to OS"})
                        ),
                        FormField(
                            id="os_version",
                            name="Operation System Version",
                            description="The version of the mobile operating system or browser the user is using.",
                            component=FormComponent(type="dotPath", props={"label": "Path to OS version"})
                        ),
                        FormField(
                            id="device_brand",
                            name="Device Brand",
                            description="The device brand that the user is using.",
                            component=FormComponent(type="dotPath", props={"label": "Path to device brand"})
                        ),
                        FormField(
                            id="device_manufacturer",
                            name="Device Manufacturer",
                            description="The device manufacturer that the user is using.",
                            component=FormComponent(type="dotPath", props={"label": "Path to device manufacturer"})
                        ),
                        FormField(
                            id="device_model",
                            name="Device Model",
                            description="The device model that the user is using.",
                            component=FormComponent(type="dotPath", props={"label": "Path to device model"})
                        ),
                        FormField(
                            id="carrier",
                            name="Carrier",
                            description="The carrier that the user is using.",
                            component=FormComponent(type="dotPath", props={"label": "Path to carrier"})
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
