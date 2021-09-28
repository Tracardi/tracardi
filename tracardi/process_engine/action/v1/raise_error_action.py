from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner

from tracardi.exceptions.exception import WorkflowException


class RaiseErrorAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'message' not in kwargs or kwargs['message'] is None:
            self.message = "Workflow stopped"
        else:
            if not isinstance(kwargs['message'], str):
                raise ValueError("Message should be string")

            self.message = kwargs['message']

    async def run(self, payload):
        raise WorkflowException(self.message)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.raise_error_action',
            className='RaiseErrorAction',
            inputs=["payload"],
            outputs=[],
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "message": None
            }

        ),
        metadata=MetaData(
            name='Throw error',
            desc='Throws an error and stops workflow.',
            type='flowNode',
            width=100,
            height=100,
            icon='stop',
            group=["Input/Output"]
        )
    )
