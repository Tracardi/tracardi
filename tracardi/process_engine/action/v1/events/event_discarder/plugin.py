from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class EventDiscarder(ActionRunner):

    async def run(self, payload: dict, in_edge=None) -> Result:
        self.event.config["save"] = False
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='EventDiscarder',
            inputs=["payload"],
            outputs=["payload"],
            version='0.7.1',
            license="MIT",
            author="Dawid Kruk"
        ),
        metadata=MetaData(
            name='Discard Event',
            desc='Discards current event - Current event will not be saved if this action is used.',
            icon='error',
            group=["Events"],
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
