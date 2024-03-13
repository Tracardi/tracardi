from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.config import Config, Token
from tracardi.process_engine.action.v1.connectors.mailchimp.service.mailchimp_audience_editor import MailChimpAudienceEditor
from tracardi.service.domain import resource as resource_db
from ..endpoints import Endpoint


def validate(config: dict):
    return Config(**config)


class MailChimpAudienceRemover(ActionRunner):

    _client: MailChimpAudienceEditor
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self._client = MailChimpAudienceEditor(
            resource.credentials.get_credentials(self, Token).token,
            self.node.on_connection_error_repeat
        )

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        emails = dot[self.config.email]
        emails = emails if isinstance(emails, list) else [emails]
        results = [
            await self._delete_or_archive(list_id=self.config.list_id.id, email_address=email) for email in emails
        ]
        for result in results:
            if result is not None:
                return Result(port="error", value={"result": results})
        return Result(port="response", value={"result": results})

    async def _delete_or_archive(self, **kwargs):
        return await self._client.delete_contact(**kwargs) if self.config.delete else \
            await self._client.archive_contact(**kwargs)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='MailChimpAudienceRemover',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.8.2',
            license="MIT + CC",
            author="Dawid Kruk, Risto Kowaczewski",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "list_id": {
                    "id": None,
                    "name": None
                },
                "email": None,
                "delete": False
            },
            manual="mailchimp_remove_from_audience_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="MailChimp resource",
                                description="Please select your MailChimp resource.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "mailchimp"})
                            ),
                            FormField(
                                id="list_id",
                                name="Mailchimp audience",
                                description="Please select your MailChimp audience.",
                                component=FormComponent(type="autocomplete", props={
                                    "label": "Audience",
                                    "endpoint": {
                                        "url": Endpoint.url(
                                            'tracardi.process_engine.action.v1.connectors.mailchimp.endpoints',
                                            'get_audiences'),
                                        "method": "post"
                                    },
                                })
                            ),
                            FormField(
                                id="email",
                                name="Contact's e-mail address",
                                description="Please provide path to contact's e-mail address.",
                                component=FormComponent(type="dotPath", props={"label": "E-mail",
                                                                               "defaultSourceValue": "profile",
                                                                               "defaultPathValue": "data.contact.email.main"
                                                                               })
                            ),
                        ]
                    ),
                    FormGroup(
                        name="For Advanced Users Only",
                        fields=[
                            FormField(
                                id="delete",
                                name="Permanently delete contact",
                                description="Please determine if plugin should permanently delete contact, or archive "
                                            "it. Please notice that if you permanently delete your contact, then you"
                                            " cannot add it again. ON switch position indicates deleting mode.",
                                component=FormComponent(type="bool", props={"label": "Permanently delete contact"})
                            )
                        ]
                    )

                ]
            )
        ),
        metadata=MetaData(
            name='Remove from audience',
            brand="MailChimp",
            desc='Removes contact to MailChimp audience or archives it.',
            icon='mailchimp',
            group=["Mailchimp"],
            tags=['mailing'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes any JSON-like object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response from MailChimp API."),
                    "error": PortDoc(desc="This port returns response from MailChimp API if an error occurs.")
                }
            )
        )
    )
