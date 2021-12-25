from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi.service.mailchimp_sender import MailChimpTransactionalSender
from tracardi_plugin_sdk.domain.result import Result
from .model.config import Config, Token
from tracardi_dot_notation.dot_template import DotTemplate
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials


def validate(config: dict):
    return Config(**config)


class TransactionalMailSender(ActionRunner):

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self._client = MailChimpTransactionalSender(credentials.get_credentials(self, output=Token).token)
        self._dot_template = DotTemplate()

    @staticmethod
    async def build(**kwargs) -> 'TransactionalMailSender':
        config = validate(kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return TransactionalMailSender(
            config,
            resource.credentials
        )

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        message = self._dot_template.render(self.config.message.content.content, dot)
        recipient_emails = dot[self.config.message.recipient]
        recipient_emails = recipient_emails if isinstance(recipient_emails, list) else [recipient_emails]
        for email in recipient_emails:
            self._client.create_message(
                from_email=self.config.sender_email,
                subject=self.config.message.subject,
                message=message,
                to_email=email,
                html_content=True if self.config.message.content.type == "text/html" else False
            )
        result = self._client.send_messages()
        return Result(port="payload", value=payload), Result(port="response", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.connectors.mailchimp_transactional.plugin',
            className='TransactionalMailSender',
            inputs=["payload"],
            outputs=["payload", "response"],
            version='0.6.0.2',
            license="MIT",
            author="Dawid Kruk",
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "sender_email": None,
                "message": {
                    "recipient": None,
                    "content": None,
                    "subject": ""
                }
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Your data",
                        fields=[
                            FormField(
                                id="source",
                                name="Mailchimp resource",
                                description="Here please provide your Mandrill resource ID. ",
                                component=FormComponent(type="resource", props={"label": "resource", "tag": "token"})
                            ),
                            FormField(
                                id="sender_email",
                                name="Sender email",
                                description="Here please provide email address, that you want to send emails from. "
                                            "It has to end with domain that is correctly registered and verified for your"
                                            " Mailchimp account. For more detail check documentation or mandrillapp.com.",
                                component=FormComponent(type="text", props={"label": "Sender email"})
                            )
                        ]
                    ),
                    FormGroup(
                        name="Message data",
                        fields=[
                            FormField(
                                id="message.recipient",
                                name="Message recipient's email",
                                description="Here we need you to provide path to email address of recipient, or "
                                            "the email address itself.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="message.subject",
                                name="Message subject",
                                description="This field needs to be filled with your email's subject.",
                                component=FormComponent(type="text", props={"label": "Subject"})
                            ),
                            FormField(
                                id="message.content",
                                name="Message content",
                                description="This field contains the body of your message. It can be either text "
                                            "or HTML content. Please notice that it cannot be JSON. You can use "
                                            "templates in both HTML and text types, so something like 'Hello "
                                            "{{profile@pii.name}}!' will result in calling the customer by their name "
                                            "in our message.",
                                component=FormComponent(type="contentInput", props={"label": "Message body"})
                            )
                        ]
                    )
                ]
            ),
            manual="mailchimp_transactional_action"
        ),
        metadata=MetaData(
            name='Send transactional e-mail',
            desc='Sends transactional MailChimp e-mail.',
            type='flowNode',
            icon='plugin',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns given payload without any changes."),
                    "response": PortDoc(desc="This port returns result of message sending attempt.")
                }
            )
        )
    )
