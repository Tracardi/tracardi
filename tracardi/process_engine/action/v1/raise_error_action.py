from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    FormFieldValidation
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
                "message": "Flow stopped due to error."
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="message",
                            name="Error message",
                            description="Provide error message.",
                            component=FormComponent(type="text", props={"label": "Message"}),
                            validation=FormFieldValidation(
                                regex=r"^(?!\s*$).+",
                                message="This field must not be empty."
                            )
                        )
                    ]
                )
            ]),
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
