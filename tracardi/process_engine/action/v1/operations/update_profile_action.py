from datetime import datetime

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner


class UpdateProfileAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None):
        self.profile.metadata.time.update = datetime.utcnow()
        self.profile.set_updated_in_workflow()
        self.profile.data.compute_anonymous_field()


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='UpdateProfileAction',
            inputs=["payload"],
            outputs=[],
            version="0.8.2",
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
