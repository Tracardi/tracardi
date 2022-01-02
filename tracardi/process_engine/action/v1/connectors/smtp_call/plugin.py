from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import Resource, ResourceCredentials
from tracardi_dot_notation.dot_accessor import DotAccessor
from tracardi_dot_notation.dot_template import DotTemplate

from .service.sendman import PostMan
from .model.smtp_configuration import Configuration, SmtpConfiguration


async def validate(config: dict) -> Configuration:
    return Configuration(**config)


class SmtpDispatcherAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'SmtpDispatcherAction':
        config = await validate(kwargs)
        source = await storage.driver.resource.load(config.source.id)  # type: Resource
        return SmtpDispatcherAction(config, source.credentials)

    def __init__(self, config: Configuration, credentials: ResourceCredentials):
        smtp_config = credentials.get_credentials(self, SmtpConfiguration)  # type: SmtpConfiguration
        self.config = config
        self.post = PostMan(smtp_config)

    async def run(self, payload):
        try:
            dot = DotAccessor(self.profile, self.session, payload, self.event, self.flow)
            template = DotTemplate()
            self.config.message.message = template.render(self.config.message.message, dot)
            self.post.send(self.config.message)
            return Result(port='payload', value={"result": payload})
        except Exception as e:
            self.console.error(repr(e))
            return Result(port='error', value={"result": {"error": repr(e)}})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SmtpDispatcherAction',
            inputs=["payload"],
            outputs=['payload', 'error'],
            init={
                "source": {
                    "id": None
                },
                'message': {
                    "send_to": None,
                    "send_from": None,
                    "reply_to": None,
                    "title": None,
                    "message": None
                }
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="source",
                            name="SMTP connection resource",
                            description="Select SMTP server resource. Credentials from selected resource will be used "
                                        "to connect the service.",
                            required=True,
                            component=FormComponent(type="resource", props={"label": "resource", "tag": "smtp"})
                        )
                    ]
                ),
                FormGroup(
                    fields=[
                        FormField(
                            id="message.send_to",
                            name="E-mail to send from",
                            description="Type path to E-mail or e-mail itself.",
                            component=FormComponent(type="dotPath", props={"defaultMode": 2})
                        ),
                        FormField(
                            id="message.send_from",
                            name="Recipient e-mail",
                            description="Type path to E-mail or e-mail itself.",
                            component=FormComponent(type="dotPath", props={"defaultSourceValue": "profile"})
                        ),
                        FormField(
                            id="message.reply_to",
                            name="Reply to e-mail",
                            description="Type path to E-mail or e-mail itself.",
                            component=FormComponent(type="dotPath", props={"defaultMode": 2})
                        ),
                        FormField(
                            id="message.title",
                            name="Subject",
                            description="Type e-mail subject.",
                            component=FormComponent(type="text", props={"label": "Subject"})
                        ),
                        FormField(
                            id="message.message",
                            name="Message",
                            description="Type e-mail message.",
                            component=FormComponent(type="textarea", props={"label": "Message"})
                        )
                    ]
                ),
            ]),

            manual="smtp_connector_action",
            version='0.6.0.1',
            license="MIT",
            author="iLLu"

        ),
        metadata=MetaData(
            name='Send e-mail via SMTP',
            desc='This plugin sends mail via defined smtp server.',
            type='flowNode',
            width=200,
            height=100,
            icon='email',
            group=["Connectors", "E-mail"]
        )
    )
