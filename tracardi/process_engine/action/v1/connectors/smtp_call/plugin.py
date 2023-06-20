from tracardi.domain.content import Content
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.storage.driver.elastic import resource as resource_db
from tracardi.domain.resource import Resource
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
        resource = await resource_db.load(config.resource.id)  # type: Resource

        smtp_config = resource.credentials.get_credentials(self, SmtpConfiguration)  # type: SmtpConfiguration
        self.config = config
        self.post = PostMan(smtp_config)

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            dot = self._get_dot_accessor(payload)
            template = DotTemplate()
            message = template.render(self.config.mail.message.content, dot)
            message_obj = Message(
                send_to=dot[self.config.mail.send_to],
                send_from=dot[self.config.mail.send_from],
                title=self.config.mail.title,
                reply_to=dot[self.config.mail.reply_to],
                message=Content(content=message, type=self.config.mail.message.type)
            )
            self.post.send(message_obj)
            return Result(port='payload', value={"result": payload})
        except Exception as e:
            self.console.error(repr(e))
            return Result(port='error', value={"result": {"error": repr(e)}})


def register() -> Plugin:
    return Plugin(
        spec=Spec(
            module=__name__,
            className='SmtpDispatcherAction',
            inputs=["payload"],
            outputs=['payload', 'error'],
            init={
                "resource": {
                    "id": "",
                    "name": ""
                },
                'mail': {
                    "send_to": "",
                    "send_from": "",
                    "reply_to": "",
                    "title": "",
                    "message": {
                        "content": "",
                        "type": "text/plain"
                    }
                }
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="resource",
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
                            id="mail.send_from",
                            name="E-mail to send from",
                            description="Type path to E-mail or e-mail itself.",
                            component=FormComponent(type="dotPath", props={"label": "E-mail"})
                        ),
                        FormField(
                            id="mail.send_to",
                            name="Recipient e-mail",
                            description="Type path to E-mail or e-mail itself.",
                            component=FormComponent(type="dotPath", props={"label": "E-mail",
                                                                           "defaultSourceValue": "profile"})
                        ),
                        FormField(
                            id="mail.reply_to",
                            name="Reply to e-mail",
                            description="Type path to E-mail or e-mail itself.",
                            component=FormComponent(type="dotPath", props={"label": "E-mail"})
                        ),
                        FormField(
                            id="mail.title",
                            name="Subject",
                            description="Type e-mail subject.",
                            component=FormComponent(type="text", props={"label": "Subject"})
                        ),
                        FormField(
                            id="mail.message",
                            name="Message",
                            description="Type e-mail message.",
                            component=FormComponent(type="contentInput", props={
                                "rows": 13,
                                "label": "Message body",
                                "allowedTypes": ["text/plain", "text/html"]
                            })
                        )
                    ]
                ),
            ]),

            manual="smtp_connector_action",
            version='0.7.3',
            license="MIT",
            author="iLLu, Risto Kowaczewski"

        ),
        metadata=MetaData(
            name='Send e-mail via SMTP',
            desc='This plugin sends mail via defined smtp server.',
            type='flowNode',
            tags=['mailing', 'email', 'mail', 'messaging'],
            icon='email',
            group=["Connectors"]
        )
    )
