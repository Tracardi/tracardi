from datetime import datetime

from email_validator import validate_email, EmailNotValidError
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.domain import resource as resource_db
from ..add_contact.model.config import Connection
from ..client import ElasticEmailClient


def validate(config: dict) -> Config:
    return Config(**config)


class ElasticEmailTransactionalMailSender(ActionRunner):

    config: Config
    credentials: Connection
    client: ElasticEmailClient
    _dot_template: DotTemplate

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=Connection)
        self.client = ElasticEmailClient(**dict(self.credentials))    # type: ElasticEmailClient
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
        valid_recipient_emails = await self.get_valid_to_emails(recipient_emails)
        validate_email(self.config.sender_email)
        email_params = {
            "charset": "utf-8",
            "from": self.config.sender_email,
            #     "fromName": todo add from name
            #     "replyTo": todo add replyname
            "isTransactional": 'true',
            "subject": self.config.message.subject,
            "to": ','.join(valid_recipient_emails),
        }
        if self.config.message.content.type == "text/html":
            email_params["bodyHtml"] = message
        else:
            email_params["bodyText"] = message

        try:
            result = await self.client.emails_post(email_params)
            return Result(port="response", value=result)
        except Exception as e:
            return Result(port="error", value={"message": str(e)})

    async def get_valid_to_emails(self, recipient_emails):
        valid_recipient_emails = []
        for email in recipient_emails:
            try:
                validate_email(email)
                valid_recipient_emails.append(email)
            except EmailNotValidError:
                self.console.warning("Recipient e-mail {} is not valid email. This e-mail was skipped.".format(email))
                continue
        return valid_recipient_emails


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ElasticEmailTransactionalMailSender',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.2',
            license="MIT + CC",
            author="Ben Ullrich",
            manual="elastic_email_transactional_action",
            init={
                "source": {
                    "id": "",
                    "name": ""
                },
                "sender_email": "",
                "message": {
                    "recipient": "",
                    "content": "",
                    "subject": "",
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
                                                        props={"label": "Resource", "tag": "elasticemail"})
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
                                component=FormComponent(type="dotPath", props={
                                    "label": "E-mail",
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
            name='Send transactional e-mail',
            brand='Elastic Email',
            desc='Sends transactional e-mail via Elastic Email based on provided data.',
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
