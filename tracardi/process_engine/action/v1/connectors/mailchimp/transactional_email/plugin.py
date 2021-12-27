from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi.service.mailchimp_sender import MailChimpTransactionalSender
from tracardi_plugin_sdk.domain.result import Result
from tracardi.process_engine.action.v1.connectors.mailchimp.transactional_email.model.config import Config, Token
from tracardi_dot_notation.dot_template import DotTemplate
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials
from email_validator import validate_email, EmailNotValidError


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

        validate_email(self.config.sender_email)

        for email in recipient_emails:

            try:
                validate_email(email)
            except EmailNotValidError:
                self.console.warning("Recipient e-mail {} is not valid email. This e-mail was skipped.".format(email))
                continue

            self._client.create_message(
                from_email=self.config.sender_email,
                subject=self.config.message.subject,
                message=message,
                to_email=email,
                html_content=True if self.config.message.content.type == "text/html" else False
            )

        result = self._client.send_messages()

        for data in result:
            for response in data:
                if 'status' not in response:
                    self.console.warning("MailChimp API did not return status.")
                    return Result(port="error", value={"result": result})
                elif response['status'] != 'sent':
                    self.console.warning(
                        "MailChimp API returned status: `{}` and error: `{}`".format(response['status'],
                                                                                     response['reject_reason']))
                    return Result(port="error", value={"result": result})

        return Result(port="response", value={"result": result})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.connectors.mailchimp.transactional_email.plugin',
            className='TransactionalMailSender',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.0.1',
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
                    "subject": None
                }
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="MailChimp resource",
                                description="Please provide your MailChimp resource ID. ",
                                component=FormComponent(type="resource", props={"label": "resource", "tag": "token"})
                            ),
                            FormField(
                                id="sender_email",
                                name="Sender e-mail",
                                description="Please provide e-mail address, that you want to send e-mails from. "
                                            "It has to end with domain that is correctly registered and verified in "
                                            "MailChimp account. For more detail check documentation or mandrillapp.com.",
                                component=FormComponent(type="text", props={"label": "Sender e-mail"})
                            )
                        ]
                    ),
                    FormGroup(
                        name="Message data",
                        fields=[
                            FormField(
                                id="message.recipient",
                                name="Message recipient's email",
                                description="Please provide path to e-mail address of a recipient, or "
                                            "the e-mail address itself.",
                                component=FormComponent(type="dotPath", props={"label": "E-mail"})
                            ),
                            FormField(
                                id="message.subject",
                                name="Message subject",
                                component=FormComponent(type="text", props={"label": "Subject"})
                            ),
                            FormField(
                                id="message.content",
                                name="Message content",
                                description="This field contains the body of your message. It can be either text "
                                            "or HTML content. You can use templates in both HTML and text types, "
                                            "something like 'Hello {{profile@pii.name}}!' will result in calling "
                                            "the customer by their name in the message text.",
                                component=FormComponent(type="contentInput", props={"label": "Message body"})
                            )
                        ]
                    )
                ]
            ),
            manual="mailchimp_transactional_action"
        ),
        metadata=MetaData(
            name='Send e-mail',
            desc='Sends transactional e-mail via MailChimp API.',
            type='flowNode',
            icon='mailchimp',
            group=["Connectors", "E-mail"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "error": PortDoc(desc="This port is triggered if the request from MailChimp API returns error."),
                    "response": PortDoc(desc="This port returns result of message sending attempt.")
                }
            )
        )
    )
