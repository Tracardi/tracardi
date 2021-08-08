import copy

from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi.process_engine.tql.condition import Condition
from tracardi.process_engine.tql.utils.dictonary import flatten


class IfAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'condition' not in kwargs:
            raise ValueError("Condition is not set. Define it in config section.")
        self.condition = kwargs['condition']

    async def run(self, payload: dict):

        try:
            flat_payload = flatten(copy.deepcopy(payload))
        except Exception as e:
            raise ValueError("Could not flatten payload. The following error occurred: `{}`".format(str(e)))

        if self.condition is None or self.condition == "please-configure-condition":
            raise ValueError("Condition is not set. Define it in config section.")

        if Condition.evaluate(self.condition, flat_payload):
            return Result(port="TRUE", value=payload)
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
            init={"condition": "please-configure-condition"},
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
            group=['Processing']
        )
    )
