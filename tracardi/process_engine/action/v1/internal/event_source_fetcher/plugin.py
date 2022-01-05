from tracardi.service.storage.driver import storage
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi_plugin_sdk.domain.result import Result


class EventSourceFetcherAction(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, payload):
        source = await storage.driver.event_source.load(self.event.source.id)
        if source is None:
            return Result(port="error", value={"message": "Source `{}` does not exist.".format(self.event.source.id)})
        return Result(port="source", value=source.dict())


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='EventSourceFetcherAction',
            inputs=["payload"],
            outputs=['source', 'error'],
            version='0.6.0.1',
            license="MIT",
            author="Risto Kowaczewski",
            init=None
        ),
        metadata=MetaData(
            name='Read event source',
            desc='This plugin reads the source that the event came from.',
            icon='inbound',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="Reads payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns source data."),
                }
            ),
        )
    )