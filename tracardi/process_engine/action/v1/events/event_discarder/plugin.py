from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result


class EventDiscarder(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, payload):
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
            desc='Discards current event - it does not get saved after workflow ends.',
            icon='error',
            group=["Flow control"],
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
