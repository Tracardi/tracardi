from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import Resource, ResourceCredentials
from tracardi.service.notation.dot_template import DotTemplate

from .service.sendman import PostMan
from .model.smtp_configuration import Configuration, SmtpConfiguration, Message


async def validate(config: dict) -> Configuration:
    return Configuration(**config)


class SmtpDispatcherAction(ActionRunner):

    post: PostMan
    config: Configuration

    async def set_up(self, init):
        config = await validate(init)
        source = await storage.driver.resource.load(config.source.id)  # type: Resource

        smtp_config = source.credentials.get_credentials(self, SmtpConfiguration)  # type: SmtpConfiguration
        self.config = config
        self.post = PostMan(smtp_config)

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            dot = self._get_dot_accessor(payload)
            template = DotTemplate()
            message = template.render(self.config.message.message, dot)
            message_obj = Message(
                send_to=dot[self.config.message.send_to],
                send_from=dot[self.config.message.send_from],
                title=self.config.message.title,
                reply_to=dot[self.config.message.reply_to],
                message=message
            )
            self.post.send(message_obj)
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
                    "id": "",
                    "name": ""
                },
                'message': {
                    "send_to": "",
                    "send_from": "",
                    "reply_to": "",
                    "title": "",
                    "message": ""
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
                            id="message.send_from",
                            name="E-mail to send from",
                            description="Type path to E-mail or e-mail itself.",
                            component=FormComponent(type="dotPath", props={"label": "E-mail"})
                        ),
                        FormField(
                            id="message.send_to",
                            name="Recipient e-mail",
                            description="Type path to E-mail or e-mail itself.",
                            component=FormComponent(type="dotPath", props={"label": "E-mail",
                                                                           "defaultSourceValue": "profile"})
                        ),
                        FormField(
                            id="message.reply_to",
                            name="Reply to e-mail",
                            description="Type path to E-mail or e-mail itself.",
                            component=FormComponent(type="dotPath", props={"label": "E-mail"})
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
            tags=['mailing'],
            width=200,
            height=100,
            icon='email',
            group=["Connectors"]
        )
    )
