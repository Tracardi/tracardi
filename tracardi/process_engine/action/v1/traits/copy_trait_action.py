from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi_dot_notation.dot_accessor import DotAccessor


class CopyTraitAction(ActionRunner):

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

        if not isinstance(dot.profile['traits']['private'], dict):
            raise ValueError("Error when setting profile@traits.private to value `{}`. Private must have key:value pair. "
                             "E.g. `name`: `{}`".format(dot.profile['traits']['private'], dot.profile['traits']['private']))

        if not isinstance(dot.profile['traits']['public'], dict):
            raise ValueError("Error when setting profile@traits.public to value `{}`. Public must have key:value pair. "
                             "E.g. `name`: `{}`".format(dot.profile['traits']['public'], dot.profile['traits']['public']))

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
            module='tracardi.process_engine.action.v1.traits.copy_trait_action',
            className='CopyTraitAction',
            inputs=['payload'],
            outputs=["payload"],
            init={
                "copy": {
                    "target1": "source1",
                    "target2": "source2",
                }
            },
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Copy/Set Trait',
            desc='Returns payload with copied/set traits.',
            type='flowNode',
            width=100,
            height=100,
            icon='copy',
            group=["Traits"]
        )
    )
