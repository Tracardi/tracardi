from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class SessionDiscarder(ActionRunner):

    async def run(self, payload: dict, in_edge=None) -> Result:
        self.tracker_payload.options["saveSession"] = False
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=SessionDiscarder.__name__,
            inputs=["payload"],
            outputs=["payload"],
            version='0.8.0',
            license="MIT + CC",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Discard Session',
            desc='Discards current session - Current session will not be saved if this action is used.',
            icon='error',
            group=["Sessions"],
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
