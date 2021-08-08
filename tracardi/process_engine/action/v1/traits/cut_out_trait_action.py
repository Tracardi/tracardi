from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi_dot_notation.dot_accessor import DotAccessor


class CutOutTraitAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'trait' not in kwargs:
            raise ValueError("Please define trait in config section.")

        if kwargs['trait'] == 'undefined':
            raise ValueError("Please define trait in config section. It has default value of undefined.")

        self.property = kwargs['trait']

    async def run(self, payload: dict):
        dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)
        return Result(port="trait", value=dot[self.property])


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.traits.cut_out_trait_action',
            className='CutOutTraitAction',
            inputs=['payload'],
            outputs=["trait"],
            init={
                "trait": "undefined"
            },
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Cut out trait',
            desc='Returns defined property from payload.',
            type='flowNode',
            width=200,
            height=100,
            icon='property',
            group=["Traits"]
        )
    )
