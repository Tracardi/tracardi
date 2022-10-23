from tracardi.service.storage.driver import storage
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from pytimeparse import parse
from .model.configuration import Configuration


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class EventCounter(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        time_span_in_sec = parse(self.config.time_span.strip("-"))

        no_of_events = await storage.driver.event.count_events_by_type(
            self.profile.id,
            self.config.event_type.id,
            time_span_in_sec
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
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            manual="event_counter_action"
        ),
        metadata=MetaData(
            name='Event counter',
            desc='This plugin reads how many events of defined type were triggered within defined time.',
            icon='event',
            group=["Events"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns number of event of given type.")
                }
            ),
            pro=True
        )
    )
