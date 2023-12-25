from tracardi.service.domain import resource as resource_db
from tracardi.domain.geo import Geo
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
        resource = await resource_db.load(id=config.source.id)  # type: Resource

        geoip2_config = GeoIpConfiguration(
            webservice=resource.credentials.get_credentials(self, output=GeoLiteCredentials)
        )
        self.client = MaxMindGeoLite2(geoip2_config)
        self.config = config

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            dot = self._get_dot_accessor(payload)

            ip = dot[self.config.ip]

            geo = await self.client.fetch(ip)

            result = {
                "city": geo.city.name,
                "country": {
                    "name": geo.country.name,
                    "code": geo.country.iso_code
                },
                "county": geo.subdivisions.most_specific.name,
                "postal": geo.postal.code,
                "latitude": geo.location.latitude,
                "longitude": geo.location.longitude,
                "location": (geo.location.longitude, geo.location.latitude)
            }

            if self.config.add_to_profile:
                self.profile.data.devices.last.geo = Geo(**result)
                self.profile.mark_for_update()

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
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="geo/geo_ip_locator",
            init={
                "source": {
                    "id": None,
                    "name": None,
                },
                "ip": "event@request.headers.x-forwarded-for",
                "add_to_profile": False
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
                        ),
                        FormField(
                            id="add_to_profile",
                            name="Add location to profile",
                            description="Add discovered location to profile's last device location.",
                            component=FormComponent(type="bool", props={"label": "Add to profile"})
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
