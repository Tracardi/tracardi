from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result

from .model.configuration import Configuration
from .service.day_night_checker import is_day


def validate(config: dict):
    return Configuration(**config)


class DayNightAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        latitude = dot[self.config.latitude]
        longitude = dot[self.config.longitude]

        if longitude and latitude:
            if is_day(longitude, latitude):
                return Result(value=payload, port="day")

            return Result(value=payload, port="night")
        else:
            return Result(value={
                "message": "No location of the profile available."
            }, port="error")

def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.time.day_night.plugin',
            className='DayNightAction',
            inputs=['payload'],
            outputs=["day", "night", "error"],
            manual='day_night_split_action',
            init={
                "latitude": "profile@data.devices.last.geo.latitude",
                "longitude": "profile@data.devices.last.geo.longitude"
            },
            version="0.8.2",
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="latitude",
                            name="Latitude",
                            description="Path to latitude data or latitude itself.",
                            component=FormComponent(type="dotPath", props={"label": "Latitude"})
                        ),
                        FormField(
                            id="longitude",
                            name="Longitude",
                            description="Path to longitude data or longitude itself.",
                            component=FormComponent(type="dotPath", props={"label": "longitude"})
                        )
                    ]
                ),
            ]),
        ),
        metadata=MetaData(
            name='Day/Night',
            desc='Splits workflow whether it is day or night in a given latitude and longitude.',
            tags=['condition'],
            icon='dark-light',
            group=["Time"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "day": PortDoc(desc="Returns input payload if it is a day."),
                    "night": PortDoc(desc="Returns input payload if it is a night"),
                    "error": PortDoc(desc="Returns error if longitude and latitude and not be found in profile."),
                }
            )
        )
    )
