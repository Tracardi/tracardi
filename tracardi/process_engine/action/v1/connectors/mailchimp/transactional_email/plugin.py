from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.mailchimp_sender import MailChimpTransactionalSender
from tracardi.process_engine.action.v1.connectors.mailchimp.transactional_email.model.config import Config, Token
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.domain import resource as resource_db
from email_validator import validate_email, EmailNotValidError


def validate(config: dict):
    return Config(**config)


class TransactionalMailSender(ActionRunner):
    _dot_template: DotTemplate
    _client: MailChimpTransactionalSender
    config: Config

    async def set_up(self, init):

        config = validate(init)
        resource = await resource_db.load(config.source.id)

        print(resource.credentials.get_credentials(self, output=Token).token)

        self.config = config
        self._client = MailChimpTransactionalSender(resource.credentials.get_credentials(self, output=Token).token)
        self._dot_template = DotTemplate()

    async def run(self, payload: dict, in_edge=None) -> Result:
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
            license="MIT + CC",
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
                                component=FormComponent(type="resource", props={"label": "resource", "tag": "mailchimp"})
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
                                component=FormComponent(type="dotPath", props={"label": "E-mail",
                                                                               "defaultSourceValue": "profile",
                                                                               "defaultPathValue": "data.contact.email.main"
                                                                               })
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
                                            "something like 'Hello {{profile@data.pii.display_name}}!' will result in calling "
                                            "the customer by their name in the message text.",
                                component=FormComponent(type="contentInput", props={
                                    "label": "Message body",
                                    "allowedTypes": ["text/plain", "text/html"]
                                })
                            )
                        ]
                    )
                ]
            ),
            manual="mailchimp_transactional_action"
        ),
        metadata=MetaData(
            name='Send e-mail',
            brand='MailChimp',
            desc='Sends transactional e-mail via MailChimp API.',
            type='flowNode',
            icon='mailchimp',
            group=["Mailchimp"],
            tags=['mailing'],
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
