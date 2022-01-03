from tracardi.domain.profile import Profile

from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi_plugin_sdk.action_runner import ActionRunner


class UpdateProfileAction(ActionRunner):

    def __init__(self, *args, **kwargs):
        pass

    async def run(self, payload):
        if self.debug is not True:
            if isinstance(self.profile, Profile):
                self.profile.operation.update = True
            else:
                if self.event.metadata.profile_less is True:
                    self.console.warning("Can not update profile when processing profile less events.")
                else:
                    self.console.error("Can not update profile. Profile is empty.")
        else:
            self.console.warning("Profile update skipped. It will not be updated when debugging.")


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.operations.update_profile_action',
            className='UpdateProfileAction',
            inputs=["payload"],
            outputs=[],
            version="0.6.0.1",
            init=None,
            manual="update_profile_action"
        ),
        metadata=MetaData(
            name='Update profile',
            desc='Updates profile in storage.',
            icon='store',
            group=["Operations"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={}
            )
        )
    )
