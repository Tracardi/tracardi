from dotty_dict import dotty
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from app.process_engine.dot_accessor import DotAccessor


class CutOutPropertyAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'property' not in kwargs:
            raise ValueError("Please define property in config section.")

        if kwargs['property'] == 'undefined':
            raise ValueError("Please define property in config section. It has default value of undefined.")

        self.property = kwargs['property']

    async def run(self, payload: dict):
        dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)
        return Result(port="property", value=dot[self.property])


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='app.process_engine.action.v1.properties.cut_out_property_action',
            className='CutOutPropertyAction',
            inputs=['payload'],
            outputs=["property"],
            init={
                "property": "undefined"
            }
        ),
        metadata=MetaData(
            name='Cut out property',
            desc='Returns defined property from payload.',
            type='flowNode',
            width=200,
            height=100,
            icon='property',
            group=["Customer Data"]
        )
    )
