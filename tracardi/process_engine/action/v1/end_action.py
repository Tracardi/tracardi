from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner


class EndAction(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, payload):
        print(self.memory)
        return None


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='EndAction',
            inputs=["payload"],
            outputs=[],
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski"

        ),
        metadata=MetaData(
            name='End',
            desc='Ends workflow.',
            icon='stop',
            group=["Input/Output"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={}
            )
        )
    )
