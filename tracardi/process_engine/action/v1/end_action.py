from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.action_runner import ActionRunner


class EndAction(ActionRunner):

    def __init__(self, **kwargs):
        pass

    async def run(self, payload):
        return None


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.end_action',
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
