from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config, EndpointConfig
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials
from tracardi.process_engine.action.v1.connectors.active_campaign.client import ActiveCampaignClient, \
    ActiveCampaignClientException
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint


def validate(config: dict) -> Config:
    return Config(**config)


class SendToActiveCampaignAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'SendToActiveCampaignAction':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return SendToActiveCampaignAction(config, resource.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.client = ActiveCampaignClient(**credentials.get_credentials(self))

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)
        self.config.fields = traverser.reshape(self.config.fields)

        try:
            result = await self.client.send_contact(self.config.fields)
            return Result(port="success", value=result)

        except ActiveCampaignClientException as e:
            return Result(port="error", value={"detail": str(e)})


class Endpoint(PluginEndpoint):

    @staticmethod
    async def get_custom_fields(config: dict) -> list:
        config = EndpointConfig(**config)
        resource = await storage.driver.resource.load(config.source.id)
        client = ActiveCampaignClient(**resource.credentials.production)
        result = await client.get_custom_fields()
        return result


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SendToActiveCampaignAction',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.3',
            license="MIT",
            author="Dawid Kruk",
            manual="add_active_campaign_contact_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "fields": {}
            },
            form=Form(groups=[FormGroup(name="Add ActiveCampaign contact", fields=[
                FormField(
                    id="source",
                    name="Resource",
                    description="Select your ActiveCampaign resource.",
                    component=FormComponent(type="resource", props={"tag": "active_campaign"})
                ),
                FormField(
                    id="fields",
                    name="Fields",
                    description="Map all fields from ActiveCampaign (email, first name, last name, custom fields) "
                                "to dotted paths. Key should be the name of the field, and value should represent the "
                                "path.",
                    component=FormComponent(type="keyValueList", props={
                        "defaultValueSource": "profile",
                        "availableValues": [
                            {"name": "First name", "id": "firstName"}, {"name": "Last name", "id": "lastName"},
                            {"name": "Phone number", "id": "phone"}, {"name": "Email address", "id": "email"},
                            {"name": "Organization ID", "id": "orgid"}, {"name": "SegmentIO ID", "id": "segmentio_id"},
                            {"name": "IP address", "id": "ip"}, {"name": "Organization", "id": "organization"},
                            {"name": "Gravatar", "id": "gravatar"}
                        ],
                        "endpoint": {
                            "method": "post",
                            "url": Endpoint.url(__name__, "get_custom_fields")
                        }
                    })
                )
            ])])
        ),
        metadata=MetaData(
            name='Add contact',
            desc='Creates or updates a contact in ActiveCampaign, according to provided configuration.',
            icon='active-campaign',
            group=["ActiveCampaign"],
            brand="ActiveCampaign",
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "success": PortDoc(desc="This port returns contact info if the action was successful."),
                    "error": PortDoc(desc="This port returns some error info if an error occurred.")
                }
            )
        )
    )
