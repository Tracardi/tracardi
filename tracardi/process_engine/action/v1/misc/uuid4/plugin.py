from uuid import uuid4

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner


class GetUuid4Action(ActionRunner):

    async def run(self, payload: dict, in_edge=None) -> Result:
        return Result(port='uuid4', value={
            "uuid4": str(uuid4())
        })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='GetUuid4Action',
            inputs=["payload"],
            outputs=['uuid4'],
            version='0.6.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='uuid4'
        ),
        metadata=MetaData(
            name='UUID4',
            desc='Generates random UUID.',
            icon='hash',
            group=["Operations"],
            tags=["hash", "id"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "uuid4": PortDoc(desc="This port returns UUID4.")
                }
            )
        )
    )
