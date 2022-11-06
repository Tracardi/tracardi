from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class DiscardProfileUpdateAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None):
        self.discard_profile_update()
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=DiscardProfileUpdateAction.__name__,
            inputs=["payload"],
            outputs=["payload"],
            version="0.7.3",
            init=None,
            manual="discardi_profile_update_action"
        ),
        metadata=MetaData(
            name='Discard profile update',
            desc='Stops update of profile in storage.',
            icon='error',
            group=["Operations"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns input payload object.")
                }
            )
        )
    )
