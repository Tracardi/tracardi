from datetime import datetime

from email_validator import validate_email, EmailNotValidError
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config, Connection
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import Resource
import ElasticEmail
from ElasticEmail.api import emails_api
from ElasticEmail.model.email_content import EmailContent
from ElasticEmail.model.body_part import BodyPart
from ElasticEmail.model.body_content_type import BodyContentType
from ElasticEmail.model.email_recipient import EmailRecipient
from ElasticEmail.model.email_message_data import EmailMessageData


def validate(config: dict) -> Config:
    return Config(**config)


class ElasticEmailBulkMailSender(ActionRunner):
    @staticmethod
    async def build(**kwargs) -> 'ElasticEmailBulkMailSender':
        config = validate(kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return ElasticEmailBulkMailSender(config, resource)

    def __init__(self, config: Config, resource: Resource):
        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=Connection)  # type: Connection
        self._dot_template = DotTemplate()

    @staticmethod
    def parse_mapping(mapping):
        for key, value in mapping.items():

            if isinstance(value, list):
                if key == "tags":
                    mapping[key] = ",".join(value)

                else:
                    mapping[key] = "|".join(value)

            elif isinstance(value, datetime):
                mapping[key] = str(value)
        return mapping

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        message = self._dot_template.render(self.config.message.content.content, dot)
        recipient_emails = dot[self.config.message.recipient]
        recipient_emails = recipient_emails if isinstance(recipient_emails, list) else [recipient_emails]
        configuration = ElasticEmail.Configuration()
        configuration.api_key['apikey'] = self.credentials.api_key
        validate_email(self.config.sender_email)
        valid_recipient_emails = []
        for email in recipient_emails:
            try:
                validate_email(email)
                valid_recipient_emails.append(email)
            except EmailNotValidError:
                self.console.warning("Recipient e-mail {} is not valid email. This e-mail was skipped.".format(email))
                continue

        email_body = []
        if self.config.message.content.type == "text/html":
            email_body.append(BodyPart(
                content_type=BodyContentType("HTML"),
                content=message,
                charset="utf-8",
            ))
        else:
            email_body.append(BodyPart(
                content_type=BodyContentType("PlainText"),
                content=message,
                charset="utf-8",
            ))
        email_transactional_message_data = EmailMessageData(
            recipients=[EmailRecipient(email) for email in recipient_emails],
            content=EmailContent(
                body=email_body,
                _from=self.config.sender_email,
                # todo maybe reply to should be added to the form and configuration?
                # reply_to="myemail@domain.com",
                subject=self.config.message.subject,
            ),
        )
        try:
            with ElasticEmail.ApiClient(configuration) as api_client:
                api_instance = emails_api.EmailsApi(api_client)
                api_response = api_instance.emails_post(email_transactional_message_data)
                return Result(port="response", value=api_response.to_dict())
        except Exception as e:
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ElasticEmailBulkMailSender',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.2',
            license="MIT",
            author="Ben Ullrich",
            manual="elastic_email_bulk_action",
            init={
                "source": {
                    "id": "",
                    "name": ""
                },
                "sender_email": "",
                "message": {
                    "recipient": "",
                    "content": "",
                    "subject": ""
                }
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Elastic Email resource",
                                description="Please select your Elastic Email resource, containing your api key",
                                component=FormComponent(type="resource",
                                                        props={"label": "Resource", "tag": "elastic-email"})
                            ),
                            FormField(
                                id="sender_email",
                                name="Sender e-mail",
                                description="Please provide e-mail address, that you want to send e-mails from. "
                                            "It has to end with domain that is correctly registered and verified in "
                                            "Elastic Email account. For more detail check documentation.",
                                component=FormComponent(type="text", props={"label": "Sender e-mail"})
                            ),
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
                                                                               "defaultPathValue": "pii.email"
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
                                            "something like 'Hello {{profile@pii.name}}!' will result in calling "
                                            "the customer by their name in the message text.",
                                component=FormComponent(type="contentInput", props={
                                    "label": "Message body",
                                    "allowedTypes": ["text/plain", "text/html"]
                                })
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Send bulk e-mails',
            brand='Elastic Email',
            desc='Sends bulk e-mail via Elastic Email based on provided data.',
            icon='email',
            group=["Elastic Email"],
            tags=['mailing'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response from Elastic Email API."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
