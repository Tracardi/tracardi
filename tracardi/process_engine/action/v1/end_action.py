from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner


class EndAction(ActionRunner):

    async def run(self, payload: dict, in_edge=None):
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
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='end'
        ),
        metadata=MetaData(
            name='End',
            desc='Ends workflow.',
            type="startNode",
            icon='stop',
            group=["Flow"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={}
            )
        )
    )
