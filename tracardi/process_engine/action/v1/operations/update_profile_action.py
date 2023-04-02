from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner


class UpdateProfileAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None):
        if self.debug is True:
            self.console.warning("Profile will not be updated in debug mode. "
                                 "Debug only test workflow and does not run "
                                 "the whole ingestion process.")
        self.update_profile()


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
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
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload object.")
                },
                outputs={}
            )
        )
    )
