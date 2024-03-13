from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, FormField, \
    FormComponent, FormGroup, Form
from tracardi.service.plugin.runner import ActionRunner
from tracardi.process_engine.action.v1.connectors.active_campaign.client import ActiveCampaignClient, \
    ActiveCampaignClientException
from .model.config import Config
from tracardi.service.domain import resource as resource_db
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class FetchActiveCampaignProfileByEmailAction(ActionRunner):

    client: ActiveCampaignClient
    config: Config

    async def set_up(self, init):
        config = Config(**init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.client = ActiveCampaignClient(**resource.credentials.get_credentials(self))
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        email = dot[self.config.email]

        try:
            result = await self.client.get_contact_by_email(email)
            return Result(port="result", value=result)

        except ActiveCampaignClientException as e:
            return Result(port="error", value={"detail": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='FetchActiveCampaignProfileByEmailAction',
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.6.3',
            license="MIT + CC",
            author="Dawid Kruk",
            init={
                "source": {
                    "id": "",
                    "name": ""
                },
                "email": None
            },
            manual="fetch_ac_contact_by_email_action",
            form=Form(groups=[FormGroup(name="Fetch ActiveCampaign contact", fields=[
                FormField(
                    id="source",
                    name="Resource",
                    description="Select your ActiveCampaign resource.",
                    component=FormComponent(type="resource", props={"tag": "activecampaign"})
                ),
                FormField(
                    id="email",
                    name="Email address",
                    description="Provide a path to the email address of the contact that you want to fetch.",
                    component=FormComponent(type="dotPath", props={"label": "Email"})
                )
            ])])
        ),
        metadata=MetaData(
            name='Fetch contact',
            desc='Fetches ActiveCampaign contact info based on given email address.',
            icon='active-campaign',
            group=["ActiveCampaign"],
            brand="ActiveCampaign",
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This port returns fetched contact info."),
                    "error": PortDoc(desc="This port returns some error info if an error occurs.")
                }
            )
        )
    )
