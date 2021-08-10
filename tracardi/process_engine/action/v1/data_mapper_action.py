from dotty_dict import dotty
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from tracardi_dot_notation.dot_accessor import DotAccessor


class DataMapperAction(ActionRunner):

    def __init__(self, **kwargs):
        self.mapping = kwargs

    async def run(self, payload):

        source = DotAccessor(self.profile, self.session, payload, self.event, self.flow)
        config = dotty(self.mapping)

        destination = dotty()
        for key, value in config.items():
            destination[key] = source[value]

        return Result(port="payload", value=destination.to_dict())


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.data_mapper_action',
            className='DataMapperAction',
            inputs=["payload"],
            outputs=['payload'],
            init={},
            manual="data_mapper_action",
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Reshape payload',
            desc='Creates new payload from provided data. Configuration defines where the data should be copied.',
            type='flowNode',
            width=200,
            height=100,
            icon='copy-property',
            group=["Processing"]
        )
    )

