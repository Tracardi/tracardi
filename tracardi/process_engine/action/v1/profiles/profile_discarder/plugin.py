from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class ProfileDiscarder(ActionRunner):

    async def run(self, payload: dict, in_edge=None) -> Result:
        self.tracker_payload.options["saveProfile"] = False
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=ProfileDiscarder.__name__,
            inputs=["payload"],
            outputs=["payload"],
            version='0.8.0',
            license="MIT + CC",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Discard Profile',
            desc='Discards current profile - Current profile will not be saved if this action is used.',
            icon='error',
            group=["Profiles"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload without any changes.")
                }
            )
        )
    )
