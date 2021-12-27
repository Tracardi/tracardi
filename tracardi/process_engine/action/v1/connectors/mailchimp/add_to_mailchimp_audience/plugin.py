from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi_plugin_sdk.action_runner import ActionRunner
from .model.config import Config, Token
from tracardi.service.mailchimp_audience_editor import MailChimpAudienceEditor
from tracardi_plugin_sdk.domain.result import Result
from tracardi_dot_notation.dict_traverser import DictTraverser
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials


def validate(config: dict):
    return Config(**config)


class MailChimpAudienceAdder(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'MailChimpAudienceAdder':
        config = validate(kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return MailChimpAudienceAdder(config, resource.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self._client = MailChimpAudienceEditor(credentials.get_credentials(self, Token).token)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)
        emails = dot[self.config.email]
        emails = emails if isinstance(emails, list) else [emails]
        merge_fields = traverser.reshape(self.config.merge_fields)
        results = [await self._update_or_add(
            list_id=self.config.list_id,
            email_address=email,
            subscribed=self.config.subscribed,
            merge_fields=merge_fields
        ) for email in emails]
        for result in results:
            if isinstance(result["status"], int) and result["status"] != 200:
                return Result(port="error", value={"result": results})
        return Result(port="response", value={"result": results})

    async def _update_or_add(self, **kwargs):
        return await self._client.update_contact(**kwargs) if self.config.update else \
            await self._client.add_contact(**kwargs)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.connectors.mailchimp.add_to_mailchimp_audience.plugin',
            className='MailChimpAudienceAdder',
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
                "merge_fields": {},
                "subscribed": False,
                "update": False
            },
            manual="add_to_mailchimp_audience_action",
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="MailChimp resource",
                                description="Please select your MailChimp resource.",
                                component=FormComponent(type="resource", props={"label": "Resource"})
                            ),
                            FormField(
                                id="list_id",
                                name="ID of your list (audience)",
                                description="Please type in your MailChimp audience ID.",
                                component=FormComponent(type="text", props={"label": "Audience ID"})
                            ),
                            FormField(
                                id="email",
                                name="Contact's email address",
                                description="Please provide path to contact's email address.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="merge_fields",
                                name="MailChimp merge fields",
                                description="Please provide key-value pairs, where key is the name of your MailChimp "
                                            "audience's merge field, and value is dot path to wanted value in payload,"
                                            " for example 'LNAME: profile@pii.surname'",
                                component=FormComponent(type="keyValueList")
                            ),
                            FormField(
                                id="subscribed",
                                name="Subscribed",
                                description="Please determine if this contact will be marked as subscribed or not. If "
                                            "not, they will receive a confirmation email form MailChimp. Please notice "
                                            "that you have to have permission from this person in order to mark them as"
                                            " subscribed while adding.",
                                component=FormComponent(type="bool")
                            ),
                            FormField(
                                id="update",
                                name="Update existing data",
                                description="Please determine if plugin is allowed to change data that already exists "
                                            "in your MailChimp audience.",
                                component=FormComponent(type="bool")
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Add to MailChimp audience',
            desc='Adds contact to MailChimp audience',
            type='flowNode',
            icon='plugin',
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
