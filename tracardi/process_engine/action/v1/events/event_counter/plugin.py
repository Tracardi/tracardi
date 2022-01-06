from tracardi.service.storage.driver import storage
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi_plugin_sdk.domain.result import Result

from .model.configuration import Configuration


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class EventCounter(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload) -> Result:
        no_of_events = await storage.driver.event.count_events_by_type(
            self.config.event_type,
            self.config.time_span
        )
        return Result(port="payload", value={"events": no_of_events})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.events.event_counter.plugin',
            className='EventCounter',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.0.1',
            license="MIT",
            author="Dawid Kruk",
            manual="event_counter_action",
            init={
                "event_type": "",
                "time_span": "-15m"
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Event counter settings",
                        description="Event counter reads how many events of defined type were triggered "
                                    "within defined time.",
                        fields=[
                            FormField(
                                id="event_type",
                                name="Event type",
                                description="Type event you would like to count.",
                                component=FormComponent(type="text", props={
                                    "label": "Event type"
                                })
                            ),
                            FormField(
                                id="time_span",
                                name="Time span",
                                description="Type time span, e.g. -15minutes.",
                                component=FormComponent(type="text", props={
                                    "label": "Time span"
                                })
                            ),
                        ]
                    )
                ])
        ),
        metadata=MetaData(
            name='Event counter',
            desc='This plugin reads how many events of defined type were triggered within defined time.',
            icon='event',
            group=["Stats"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns number of event of given type.")
                }
            )
        )
    )
