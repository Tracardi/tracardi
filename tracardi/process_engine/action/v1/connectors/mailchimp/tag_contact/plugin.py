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


class MailChimpContactTagger(ActionRunner):

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
        email = dot[self.config.email]
        tags = [tag.strip() for tag in self.config.tags.split(',')]
        try:
            results = await self._client.tag_contact(
                list_id=self.config.list_id.id,
                email_address=email,
                tag_names=tags)
            return Result(port="response", value={"result": results})
        except Exception as e:
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=MailChimpContactTagger.__name__,
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.8.2',
            license="MIT + CC",
            author="Risto Kowaczewski",
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
                "tags": ""
            },
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
                            FormField(
                                id="tags",
                                name="Tags",
                                description="Please type comma separated tags for this email.",
                                component=FormComponent(type="text", props={"label": "Tags"})
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Tag e-mail',
            brand="MailChimp",
            desc='Tags delivered e-mail with defined tags.',
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
