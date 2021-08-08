from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner


class ReadEventAction(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, void):
        return Result(port="event", value=self.event.dict())


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.read_event_action',
            className='ReadEventAction',
            inputs=['void'],
            outputs=["event"],
            init=None,
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Read event',
            desc='Loads event into workflow.',
            type='flowNode',
            width=200,
            height=100,
            icon='event',
            group=["Read"]
        )
    )
