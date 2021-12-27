from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from .model.config import Config, Token
from tracardi.process_engine.action.v1.connectors.mailchimp.service.mailchimp_audience_editor import MailChimpAudienceEditor
from tracardi_plugin_sdk.domain.result import Result
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials


def validate(config: dict):
    return Config(**config)


class MailChimpAudienceRemover(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'MailChimpAudienceRemover':
        config = validate(kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return MailChimpAudienceRemover(config, resource.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self._client = MailChimpAudienceEditor(credentials.get_credentials(self, Token).token)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        emails = dot[self.config.email]
        emails = emails if isinstance(emails, list) else [emails]
        results = [
            await self._delete_or_archive(list_id=self.config.list_id, email_address=email) for email in emails
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
            version='0.6.0.1',
            license="MIT",
            author="Dawid Kruk",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "list_id": None,
                "email": None,
                "delete": False
            },
            manual="remove_from_mailchimp_audience_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="MailChimp resource",
                                description="Please select your MailChimp resource.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "token"})
                            ),
                            FormField(
                                id="list_id",
                                name="ID of your e-mail list (audience)",
                                description="Please type in your MailChimp audience ID.",
                                component=FormComponent(type="text", props={"label": "Audience ID"})
                            ),
                            FormField(
                                id="email",
                                name="Contact's email address",
                                description="Please provide path to contact's email address.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
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
            name='Remove from MailChimp audience',
            desc='Removes contact to MailChimp audience or archives it.',
            icon='mailchimp',
            group=["Connectors"],
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
