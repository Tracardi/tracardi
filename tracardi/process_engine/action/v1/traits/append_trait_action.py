from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi.domain.event import Event
from tracardi.domain.profile import Profile
from tracardi.domain.session import Session
from tracardi_dot_notation.dot_accessor import DotAccessor


class AppendTraitAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'append' not in kwargs:
            raise ValueError("Please define `append` in config section.")
        if not isinstance(kwargs['append'], dict):
            raise ValueError("Please define `append` as dictionary not {}.".format(type(kwargs['append'])))

        self.mapping = kwargs['append']

    async def run(self, payload: dict):

        dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)
        for destination, value in self.mapping.items():
            if destination in dot:
                if not isinstance(dot[destination], list):
                    dot[destination] = [dot[destination]]

                if value not in dot[destination]:
                    dot[destination].append(value)
            else:
                dot[destination] = value

        if not isinstance(dot.profile['traits']['private'], dict):
            raise ValueError("Error when appending profile@traits.private to value `{}`. Private must have key:value pair. "
                             "E.g. `name`: `{}`".format(dot.profile['traits']['private'], dot.profile['traits']['private']))

        if not isinstance(dot.profile['traits']['public'], dict):
            raise ValueError("Error when appending profile@traits.public to value `{}`. Public must have key:value pair. "
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
            module='tracardi.process_engine.action.v1.traits.append_trait_action',
            className='AppendTraitAction',
            inputs=['payload'],
            outputs=["payload"],
            init={
                "append": {
                    "target1": "source1",
                    "target2": "source2",
                }
            },
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Append Trait',
            desc='Appends trait if it a value already exists or sets trait if it does not.',
            type='flowNode',
            width=100,
            height=100,
            icon='append',
            group=["Traits"]
        )
    )
