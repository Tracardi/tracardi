from datetime import datetime

from email_validator import validate_email, EmailNotValidError

from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.notation.dot_template import DotTemplate
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config, Token
from tracardi.service.domain import resource as resource_db
from ..client import SendgridClient


def validate(config: dict) -> Config:
    return Config(**config)


class SendgridContactAdder(ActionRunner):
    config: Config
    credentials: Token
    client: SendgridClient
    _dot_template: DotTemplate

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=Token)
        self.client = SendgridClient(**dict(self.credentials))
        self.client.set_retries(self.node.on_connection_error_repeat)
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
        validate_email(dot[self.config.email])
        traverser = DictTraverser(dot)
        mapping = traverser.reshape(self.config.additional_mapping)
        mapping = self.parse_mapping(mapping)

        email_params = {
            "contacts": [{
                "email": dot[self.config.email],
                **mapping
            }]}
        if self.config.list_ids:
            email_params["list_ids"] = self.config.list_ids.split(',')
        try:
            result = await self.client.add_contact_to_list(email_params)
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
            className='SendgridContactAdder',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.2',
            license="MIT + CC",
            author="Ben Ullrich",
            manual="sendgrid_add_contact_to_list",
            init={
                "source": {
                    "id": "",
                    "name": ""
                },
                "email": None,
                "list_ids": None,
                "additional_mapping": {},
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Token resource",
                                description="Please select your Token resource, containing your api key",
                                component=FormComponent(type="resource",
                                                        props={"label": "Resource", "tag": "sendgrid"})
                            ),
                            FormField(
                                id="email",
                                name="Email address",
                                description="Please type in the path to the email address for your new contact.",
                                component=FormComponent(type="dotPath", props={"label": "Email",
                                                                               "defaultSourceValue": "profile",
                                                                               "defaultPathValue": "data.contact.email.main"
                                                                               })
                            ),
                            FormField(
                                id="list_ids",
                                name="List Ids",
                                description="The list ids you want them added to",
                                component=FormComponent(type="text", props={"label": "List Ids"})
                            ),
                            FormField(
                                id="additional_mapping",
                                name="Additional fields",
                                description="You can add some more fields to your contact. Just type in the alias of "
                                            "the field as key, and a path as a value for this field. This is fully "
                                            "optional. (Example: surname: profile@pii.surname",
                                component=FormComponent(type="keyValueList", props={"label": "Fields"})
                            ),
                        ]
                    ),
                ]
            )
        ),
        metadata=MetaData(
            name='Add Contact to list',
            brand='Sendgrid',
            desc='Sends bulk e-mail via Sendgrid based on provided data.',
            icon='email',
            group=["Sendgrid"],
            tags=['mailing'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response from Sendgrid API."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
