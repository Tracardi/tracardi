from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.plugin.domain.config import PluginConfig


class Configuration(PluginConfig):
    type: str
    message: str


def validate(config: dict):
    return Configuration(**config)


class LogAction(ActionRunner):

    config: Configuration

    async def set_up(self, init):
        self.config = validate(init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()
        message = template.render(self.config.message, dot)

        if self.config.type == 'warning':
            self.console.warning(message)
        elif self.config.type == 'error':
            self.console.error(message)
        elif self.config.type == 'info':
            self.console.log(message)
        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='LogAction',
            inputs=["payload"],
            outputs=['payload'],
            version='0.6.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "type": "warning",
                "message": "<log-message>"
            },
            manual="log_message_action",
            form=Form(
                groups=[FormGroup(name="Log message plugin", fields=[
                    FormField(
                        id="type",
                        name="Message type",
                        description="Select type of the message that you want to log.",
                        component=FormComponent(type="select", props={"items": {
                            "warning": "Warning",
                            "error": "Error",
                            "info": "Info"
                        }, "initValue": "warning"})
                    ),
                    FormField(
                        id="message",
                        name="Message",
                        description="Provide a message that you want to log. You can use dot template here.",
                        component=FormComponent(type="textarea", props={"label": "Message"})
                    )
                ])]
            )
        ),
        metadata=MetaData(
            name='Log message',
            desc='Logs message to flow log.',
            icon='error',
            group=["Error reporting"],
            purpose=['collection', 'segmentation'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port return input payload.")
                }
            )
        )
    )
