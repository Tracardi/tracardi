from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, FormGroup, Form, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from .model.configuration import PluginConfiguration, WeatherResult
from .service.weather_client import AsyncWeatherClient


def validate(config: dict) -> PluginConfiguration:
    return PluginConfiguration(**config)


class WeatherAction(ActionRunner):

    client: AsyncWeatherClient
    config: PluginConfiguration

    async def set_up(self, init):
        self.config = validate(init)
        self.client = AsyncWeatherClient(self.config.system.upper())

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            city = self.config.city

            dot = self._get_dot_accessor(payload)
            city = dot[city]
            result = WeatherResult()

            weather = await self.client.fetch(city)

            result.temperature = weather.current.temperature
            result.humidity = weather.current.humidity
            result.wind_speed = weather.current.wind_speed
            result.description = weather.current.description

            return Result(port="weather", value=result.model_dump())

        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={"payload": payload, "error": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='WeatherAction',
            inputs=["payload"],
            outputs=["weather", "error"],
            version='0.6.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="weather_action",
            init={
                "system": "C",
                "city": None
            },
            form=Form(groups=[
                FormGroup(
                    name="Weather configuration",
                    fields=[
                        FormField(
                            id="system",
                            name="Metric system",
                            description="Select metric system.",
                            component=FormComponent(type="select", props={
                                "label": "Metric system",
                                "items": {
                                    "C": "Celsius",
                                    "F": "Fahrenheit"
                                }
                            })
                        ),
                        FormField(
                            id="city",
                            name="City",
                            description="Type city or path to city data.",
                            component=FormComponent(type="dotPath", props={})
                        )
                    ])
            ]),
        ),
        metadata=MetaData(
            name='MSN Weather service',
            desc='Retrieves weather information.',
            icon='weather',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "weather": PortDoc(desc="Returns weather conditions."),
                    "error": PortDoc(desc="Gets triggered if an error occurs.")
                }
            )
        )
    )
