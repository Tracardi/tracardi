from datetime import datetime

from email_validator import validate_email, EmailNotValidError
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import Resource
import ElasticEmail
from ElasticEmail.api import emails_api
from ElasticEmail.model.email_content import EmailContent
from ElasticEmail.model.body_part import BodyPart
from ElasticEmail.model.body_content_type import BodyContentType
from ElasticEmail.model.transactional_recipient import TransactionalRecipient
from ElasticEmail.model.email_transactional_message_data import EmailTransactionalMessageData

from .model.config import Connection


def validate(config: dict) -> Config:
    return Config(**config)


class ElasticEmailTransactionalMailSender(ActionRunner):
    @staticmethod
    async def build(**kwargs) -> 'ElasticEmailTransactionalMailSender':
        config = validate(kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return ElasticEmailTransactionalMailSender(config, resource)

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
        message = self._dot_template.render(self.config.message.content, dot)
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

        email_body = [
            BodyPart(
                content_type=BodyContentType("PlainText"),
                content=message,
                charset="utf-8",
            )
        ]
        email_transactional_message_data = EmailTransactionalMessageData(
            recipients=TransactionalRecipient(
                to=recipient_emails,
            ),
            content=EmailContent(
                body=email_body,
                _from=self.config.sender_email,
                # reply_to="myemail@domain.com",
                subject=self.config.message.subject,
            ),
        )
        try:
            with ElasticEmail.ApiClient(configuration) as api_client:
                api_instance = emails_api.EmailsApi(api_client)

                api_response = api_instance.emails_transactional_post(email_transactional_message_data)
                return Result(port="response", value=api_response.to_dict())
        except Exception as e:
            # except ElasticEmail.ApiException as e:
            return Result(port="error", value={"error": str(e), "msg": ""})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ElasticEmailTransactionalMailSender',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.2',
            license="MIT",
            author="Ben Ullrich",
            manual="elastic_email_transactional_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "sender_email": None,
                "message": {
                    "recipient": None,
                    "content": None,
                    "subject": None,
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
                                    "defaultSourceValue": "event",
                                    "defaultPathValue": "properties.emailAddress"
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
                                component=FormComponent(type="textarea", props={"label": "Message body"})
                                # component=FormComponent(type="contentInput", props={"label": "Message body"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Send e-mail Transactional',
            brand='Elastic Email',
            desc='Sends transactional e-mail via Elastic Email based on provided data.',
            icon='elastic-email',
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
