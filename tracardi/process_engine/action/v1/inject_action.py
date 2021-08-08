from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class InjectAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'inject' not in kwargs:
            raise ValueError("Inject value not defined. Please define inject key.")
        self.value = kwargs['inject']

    async def run(self, void):
        return Result(value=self.value, port="value")


def register() -> Plugin:
    return Plugin(
        start=True,
        debug=True,
        spec=Spec(
            module='tracardi.process_engine.action.v1.inject_action',
            className='InjectAction',
            inputs=[],
            outputs=["value"],
            init={"inject": {}},
            manual='inject_action',
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Inject',
            desc='Injector.',
            keywords=['start node'],
            type='flowNode',
            width=100,
            height=100,
            icon='json',
            group=["Input/Output"]
        )
    )
