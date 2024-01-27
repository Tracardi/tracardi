from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.storage.mysql.mapping.event_source_mapping import map_to_event_source
from tracardi.service.storage.mysql.service.event_source_service import EventSourceService


class EventSourceFetcherAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None) -> Result:
        ess = EventSourceService()
        source = (await ess.load_by_id_in_deployment_mode(self.event.source.id)).map_to_object(map_to_event_source)
        if source is None:
            return Result(port="error", value={"message": "Source `{}` does not exist.".format(self.event.source.id)})
        return Result(port="source", value=source.model_dump())


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='EventSourceFetcherAction',
            inputs=["payload"],
            outputs=['source', 'error'],
            version='0.8.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='get_event_source',
            init=None
        ),
        metadata=MetaData(
            name='Get event source',
            desc='This plugin reads the source that the event came from.',
            icon='inbound',
            keywords=['input'],
            group=["Input/Output"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns source data."),
                }
            )
        )
    )