from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner

from tracardi.exceptions.exception import WorkflowException
from tracardi.service.plugin.domain.config import PluginConfig


class ErrorConfiguration(PluginConfig):
    message: str = "Workflow stopped"


def validate(config: dict) -> ErrorConfiguration:
    return ErrorConfiguration(**config)


class RaiseErrorAction(ActionRunner):

    config: ErrorConfiguration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None):
        raise WorkflowException(self.config.message)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.raise_error_action',
            className='RaiseErrorAction',
            inputs=["payload"],
            outputs=[],
            version='0.6.0.1',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "message": "Flow stopped due to error."
            },
            manual="throw_error_action",
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="message",
                            name="Error message",
                            description="Provide error message.",
                            component=FormComponent(type="text", props={"label": "Message"})
                        )
                    ]
                )
            ]),
        ),
        metadata=MetaData(
            name='Throw error',
            desc='Throws an error and stops workflow.',
            icon='error',
            group=["Error reporting"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON like object.")
                },
                outputs={}
            )
        )
    )
