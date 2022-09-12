from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import Resource
from tracardi.process_engine.action.v1.connectors.hubspot.client import HubSpotClient, HubSpotClientException, \
    HubSpotClientAuthException
from tracardi.exceptions.exception import StorageException


def validate(config: dict) -> Config:
    return Config(**config)


class HubSpotCompanyGetter(ActionRunner):

    resource: Resource
    config: Config
    client: HubSpotClient

    async def set_up(self, init):
        config = validate(init)
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.resource = resource
        self.client = HubSpotClient(**resource.credentials.get_credentials(self, None))
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            result = await self.client.get_company(self.config.company_id)
            return Result(port="response", value=result)

        except HubSpotClientAuthException:
            try:
                if self.config.is_token_got is False:
                    await self.client.get_token()

                await self.client.update_token()

                result = await self.client.get_company(self.config.company_id)

                if self.debug:
                    self.resource.credentials.test = self.client.credentials
                else:
                    self.resource.credentials.production = self.client.credentials
                await storage.driver.resource.save_record(self.resource)

                return Result(port="response", value=result)

            except HubSpotClientAuthException as e:
                return Result(port="error", value={"message": str(e), "msg": ""})

            except StorageException as e:
                return Result(port="error", value={"message": "Plugin was unable to update credentials.", "msg": str(e)})

            except HubSpotClientException as e:
                return Result(port="error", value={"message": "HubSpot API error", "msg": str(e)})

        except HubSpotClientException as e:
            return Result(port="error", value={"message": "HubSpot API error", "msg": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='HubSpotCompanyGetter',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.2',
            license="MIT",
            author="Marcin Gaca",
            manual="get_hubspot_company_action",
            init={
                "source": {
                    "id": "",
                    "name": ""
                },
                "is_token_got": True,
                "company_id": None,
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="HubSpot resource",
                                description="Please select your HubSpot resource, containing your client id and "
                                            "client secret.\n"
                                            "If you haven't got access token yet, you also should select your "
                                            "redirect url and your code.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "hubspot"})
                            ),
                            FormField(
                                id="is_token_got",
                                name="Token",
                                component=FormComponent(type="bool", props={"label": "I've already got a token."}),
                            ),
                            FormField(
                                id="company_id",
                                name="Company id",
                                description="Please write an id of the company you want to get.",
                                component=FormComponent(type="text", props={"label": "Company id"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Get company by Id',
            brand="Hubspot",
            desc='Gets a company from HubSpot based on provided company id.',
            icon='hubspot',
            group=["Hubspot"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response from HubSpot API."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
