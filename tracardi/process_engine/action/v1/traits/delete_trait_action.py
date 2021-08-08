from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi.domain.profile import Profile
from tracardi_dot_notation.dot_accessor import DotAccessor


class DeleteTraitAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'delete' not in kwargs:
            raise ValueError("Please define delete in config section.")
        if not isinstance(kwargs['delete'], list):
            raise ValueError("Please define delete as list not {}.".format(type(kwargs['delete'])))

        self.delete = kwargs['delete']

    async def run(self, payload: dict):

        dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)

        for value in self.delete:
            del dot[value]

        profile = Profile(**dot.profile)

        self.profile.replace(profile)

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.traits.delete_trait_action',
            className='DeleteTraitAction',
            inputs=['payload'],
            outputs=["payload"],
            init={
                "delete": [
                    "payload@undefied",
                    "profile@undefined",
                ]
            },
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Delete Trait',
            desc='Deletes traits from profile or payload. Accepts dotted notation as definition of a filed to be '
                 'deleted. Returns payload.',
            type='flowNode',
            width=100,
            height=100,
            icon='remove',
            group=["Traits"]
        )
    )
