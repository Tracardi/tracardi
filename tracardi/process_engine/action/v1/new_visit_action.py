from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result


class NewVisitAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, void):
        if self.session.operation.new:
            return Result(port="TRUE", value=True)

        return Result(port="FALSE", value=False)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.new_visit_action',
            className='NewVisitAction',
            inputs=["void"],
            outputs=['TRUE', 'FALSE'],
            init=None,
            manual="new_visit_action",
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='New visit',
            desc='If new visit then it returns true on TRUE output, otherwise returns false on FALSE port.',
            keywords=['condition'],
            type='flowNode',
            width=200,
            height=100,
            icon='question',
            group=["Processing"]
        )
    )
