from tracardi.service.storage.driver import storage
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, \
    Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from pytimeparse import parse
from .model.configuration import Configuration


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class EventAggregator(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        time_span_in_sec = parse(self.config.time_span.strip("-"))
        if self.profile.id == '@debug-profile-id':
            self.console.warning(
                f"Please load correct profile. This plug-in may not find data for profile {self.profile.id}."
                f"Reason for this may be that you did not define an event type in the start node in the Debugging "
                f"configuration section.")

        no_of_events = await storage.driver.event.aggregate_event_by_field_within_time(
            self.profile.id,
            self.config.field.id,
            time_span_in_sec
        )
        return Result(port="payload", value={"events": no_of_events})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='EventAggregator',
            inputs=["payload"],
            outputs=['payload'],
            version='0.7.0',
            license="Tracardi Pro",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Event aggregator',
            desc='This plugin aggregates and counts events by defined field within defined time.',
            icon='event',
            group=["Events"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns the aggregation result.")
                }
            ),
            pro=True
        )
    )
