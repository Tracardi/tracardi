from tracardi_dot_notation.dict_traverser import DictTraverser
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from tracardi_dot_notation.dot_accessor import DotAccessor


class ReshapePayloadAction(ActionRunner):

    def __init__(self, **kwargs):
        self.mapping_template = kwargs

    async def run(self, payload):

        if not isinstance(payload, dict):
            self.console.warning("Payload is not dict that is why you will not be able to read it. ")

        source = DotAccessor(
            self.profile,
            self.session,
            payload,
            self.event,
            self.flow)

        traverser = DictTraverser(source)
        result = traverser.reshape(reshape_template=self.mapping_template)

        return Result(port="payload", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.traits.reshape_payload_action',
            className='ReshapePayloadAction',
            inputs=["payload"],
            outputs=['payload'],
            init={},
            manual="reshape_payload_action",
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
            group=["Traits"]
        )
    )

