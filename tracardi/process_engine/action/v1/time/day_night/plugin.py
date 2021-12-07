import re
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result

from .model.configuration import Configuration
from .service.day_night_checker import is_day


def validate(config: dict):
    return Configuration(**config)


class DayNightAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        latitude = dot[self.config.latitude]
        longitude = dot[self.config.longitude]

        if is_day(longitude, latitude):
            return Result(value=payload, port="day"), Result(value=None, port="night")

        return Result(value=None, port="day"), Result(value=payload, port="night")


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.time.day_night.plugin',
            className='DayNightAction',
            inputs=['payload'],
            outputs=["day", "night"],
            manual='day_night_split_action',
            init={
                "latitude": None,
                "longitude": None
            },
            version="0.6.0.1",
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
            desc='Splits workflow whether it is day or night in a given latitude, longitude.',
            type='flowNode',
            width=200,
            height=100,
            icon='dark-light',
            group=["Time"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "day": PortDoc(desc="Returns input payload if it is a day."),
                    "night": PortDoc(desc="Returns input payload if it is a night"),
                }
            )
        )
    )
