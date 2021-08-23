from tracardi_dot_notation.dot_accessor import DotAccessor
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi.process_engine.tql.condition import Condition


class IfAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'condition' not in kwargs:
            raise ValueError("Condition is not set. Define it in config section.")
        self.condition = kwargs['condition']

    async def run(self, payload: dict):

        if self.condition is None:
            raise ValueError("Condition is not set. Define it in config section.")

        dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)

        if Condition.evaluate(self.condition, dot):
            return Result(port="TRUE", value=payload), Result(port="FALSE", value=None)
        else:
            return Result(port="FALSE", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.if_action',
            className='IfAction',
            inputs=["payload"],
            outputs=["TRUE", "FALSE"],
            init={"condition": None},
            manual="if_action",
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='If',
            desc='This a conditional action that conditionally runs a branch of workflow.',
            keywords=['condition'],
            type='flowNode',
            width=200,
            height=100,
            icon='if',
            editor='text',
            group=['Conditions']
        )
    )
