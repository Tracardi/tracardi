from tracardi.domain.resources.token import Token
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.config import Config
from tracardi.process_engine.action.v1.connectors.mailchimp.service.mailchimp_audience_editor import MailChimpAudienceEditor
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.domain import resource as resource_db
from ..endpoints import Endpoint


def validate(config: dict):
    return Config(**config)


class MailChimpAudienceAdder(ActionRunner):

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

        traverser = DictTraverser(dot)
        emails = dot[self.config.email]
        emails = emails if isinstance(emails, list) else [emails]
        merge_fields = traverser.reshape(self.config.merge_fields)

        results = [await self._update_or_add(
            list_id=self.config.list_id.id,
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
            module=__name__,
            className='MailChimpAudienceAdder',
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
                "merge_fields": {},
                "subscribed": False,
                "update": False
            },
            manual="mailchimp_add_to_audience_action",
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
                                description="Please provide path to contact's email address.",
                                component=FormComponent(type="dotPath", props={"label": "E-mail",
                                                                               "defaultSourceValue": "profile",
                                                                               "defaultPathValue": "data.contact.email.main"})
                            ),
                            FormField(
                                id="merge_fields",
                                name="MailChimp merge fields",
                                description="Please provide key-value pairs, where the key is the name of your MailChimp "
                                            "audience's merge field, and a value is dot path to data in the payload,"
                                            " for example 'LNAME: profile@pii.surname'",
                                component=FormComponent(type="keyValueList")
                            ),
                            FormField(
                                id="subscribed",
                                name="Subscribed",
                                description="Please determine if this contact will be marked as subscribed. Unsubscribed "
                                            "user will receive a confirmation e-mail from MailChimp. Please notice "
                                            "that the user must grant you the permission to send them a message.",
                                component=FormComponent(type="bool", props={"label": "Mark as subscribed"})
                            ),
                            FormField(
                                id="update",
                                name="Update existing data",
                                description="Please determine if plugin is allowed to update data that already exists "
                                            "in your MailChimp audience.",
                                component=FormComponent(type="bool", props={"label": "Update when data exists."})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Add to audience',
            brand="MailChimp",
            desc='Adds contact to MailChimp audience',
            icon='mailchimp',
            group=["Mailchimp"],
            tags=['mailing'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response from MailChimp API."),
                    "error": PortDoc(desc="This port returns response from MailChimp API if an error occurs.")
                }
            )
        )
    )
