from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result
from tracardi_plugin_sdk.action_runner import ActionRunner

from app.domain.event import Event
from app.domain.profile import Profile
from app.domain.session import Session
from app.process_engine.dot_accessor import DotAccessor


class DeletePropertyAction(ActionRunner):

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
            module='app.process_engine.action.v1.properties.delete_property_action',
            className='DeletePropertyAction',
            inputs=['payload'],
            outputs=["payload"],
            init={
                "delete": [
                    "payload@undefied",
                    "profile@undefined",
                ]
            }
        ),
        metadata=MetaData(
            name='Delete Property',
            desc='Returns payload with deleted properties.',
            type='flowNode',
            width=100,
            height=100,
            icon='remove',
            group=["Customer Data"]
        )
    )
