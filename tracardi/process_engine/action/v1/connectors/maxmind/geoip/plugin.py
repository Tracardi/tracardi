from tracardi.service.storage.driver import storage
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, FormGroup, FormField, FormComponent, Form, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.domain.resource import Resource
from .model.maxmind_geolite2_client import GeoIpConfiguration, \
    PluginConfiguration, MaxMindGeoLite2, GeoLiteCredentials


def validate(config: dict) -> PluginConfiguration:
    return PluginConfiguration(**config)


class GeoIPAction(ActionRunner):

    config: PluginConfiguration
    client: MaxMindGeoLite2

    async def set_up(self, init):
        config = validate(init)
        resource = await storage.driver.resource.load(id=config.source.id)  # type: Resource

        geoip2_config = GeoIpConfiguration(
            webservice=resource.credentials.get_credentials(self, output=GeoLiteCredentials)
        )
        self.client = MaxMindGeoLite2(geoip2_config)
        self.config = config

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            dot = self._get_dot_accessor(payload)

            ip = dot[self.config.ip]

            location = await self.client.fetch(ip)

            result = {
                "city": location.city.name,
                "country": {
                    "name": location.country.name,
                    "code": location.country.iso_code
                },
                "county": location.subdivisions.most_specific.name,
                "postal": location.postal.code,
                "latitude": location.location.latitude,
                "longitude": location.location.longitude
            }
            return Result(port="location", value=result)
        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={"payload": payload, "error": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className="GeoIPAction",
            inputs=["payload"],
            outputs=["location", "error"],
            version='0.6.1',
            license="MIT",
            author="Risto Kowaczewski",
            manual="geo/geo_ip_locator",
            init={
                "source": {
                    "id": None,
                    "name": None,
                },
                "ip": "event@request.ip"
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="source",
                            name="Maxmind Geolite2 connection resource",
                            description="Select Maxmind Geolite2 server resource. Credentials from selected resource "
                                        "will be used to connect the service.",
                            required=True,
                            component=FormComponent(type="resource", props={"label": "resource", "tag": "geo-locator"})
                        )
                    ]
                ),
                FormGroup(
                    fields=[
                        FormField(
                            id="ip",
                            name="Path to ip",
                            description="Type path to IP data or IP address itself.",
                            component=FormComponent(type="dotPath", props={"label": "IP address"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='GeoIp service',
            brand='MaxMind',
            desc='This plugin converts IP to location information.',
            icon='location',
            group=["Location"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "location": PortDoc(desc="Returns location."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
