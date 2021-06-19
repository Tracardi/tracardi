from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from app.domain.event import Event
from app.domain.profile import Profile
from app.domain.session import Session
from app.process_engine.dot_accessor import DotAccessor


class CopyPropertyAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'copy' not in kwargs:
            raise ValueError("Please define copy in config section.")
        if not isinstance(kwargs['copy'], dict):
            raise ValueError("Please define copy as dictionary not {}.".format(type(kwargs['copy'])))

        self.mapping = kwargs['copy']

    async def run(self, payload: dict):

        dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)

        for destination, value in self.mapping.items():
            dot[destination] = value

        profile = Profile(**dot.profile)
        event = Event(**dot.event)
        session = Session(**dot.session)

        self.profile.replace(profile)
        self.session.replace(session)
        self.event.replace(event)

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='app.process_engine.action.v1.properties.copy_property_action',
            className='CopyPropertyAction',
            inputs=['payload'],
            outputs=["payload"],
            init={
                "copy": {
                    "target1": "source1",
                    "target2": "source2",
                }
            }
        ),
        metadata=MetaData(
            name='Copy Property',
            desc='Returns payload with copied properties.',
            type='flowNode',
            width=100,
            height=100,
            icon='copy',
            group=["Customer Data"]
        )
    )
