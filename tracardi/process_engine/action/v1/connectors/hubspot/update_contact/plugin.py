from tracardi.service.notation.dict_traverser import DictTraverser
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

from datetime import datetime


def validate(config: dict) -> Config:
    return Config(**config)


class HubSpotContactUpdater(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'HubSpotContactUpdater':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return HubSpotContactUpdater(config, resource)

    def __init__(self, config: Config, resource: Resource):
        self.config = config
        self.resource = resource
        self.client = HubSpotClient(**self.resource.credentials.get_credentials(self, None))

    def parse_mapping(self):
        for key, value in self.config.properties.items():

            if isinstance(value, list):
                if key == "tags":
                    self.config.properties[key] = ",".join(value)

                else:
                    self.config.properties[key] = "|".join(value)

            elif isinstance(value, datetime):
                self.config.properties[key] = str(value)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)

        self.config.properties = traverser.reshape(self.config.properties)
        self.parse_mapping()

        try:
            result = await self.client.update_contact(
                    self.config.contact_id,
                    self.config.properties
                )
            return Result(port="response", value=result)

        except HubSpotClientAuthException:
            try:
                if self.config.is_token_got is False:
                    await self.client.get_token()

                await self.client.update_token()

                result = await self.client.update_contact(
                    self.config.contact_id,
                    self.config.properties
                )

                if self.debug:
                    self.resource.credentials.test = self.client.credentials
                else:
                    self.resource.credentials.production = self.client.credentials
                await storage.driver.resource.save_record(self.resource)

                return Result(port="response", value=result)

            except HubSpotClientAuthException as e:
                return Result(port="error", value={"error": str(e), "msg": ""})

            except StorageException as e:
                return Result(port="error", value={"error": "Plugin was unable to update credentials.", "msg": str(e)})

            except HubSpotClientException as e:
                return Result(port="error", value={"error": "HubSpot API error", "msg": str(e)})

        except HubSpotClientException as e:
            return Result(port="error", value={"error": "HubSpot API error", "msg": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='HubSpotContactUpdater',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT",
            author="Marcin Gaca",
            manual="update_hubspot_contact_action",
            init={
                "source": {
                    "client_id": None,
                    "client_secret": None,
                    "refresh_token": None,
                    "redirect_uri": None,
                    "code": None,
                },
                "is_token_got": True,
                "contact_id": None,
                "properties": [],
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
                                id="contact_id",
                                name="Contact id",
                                description="Please write an id of the contact you want to update.",
                                component=FormComponent(type="text", props={"label": "Contact id"})
                            ),
                            FormField(
                                id="properties",
                                name="Properties fields",
                                description="You can add some more fields to your contact. Just type in the alias of "
                                            "the field as key, and a path as a value for this field. This is fully "
                                            "optional.",
                                component=FormComponent(type="keyValueList", props={"label": "Fields"})
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='HubSpot: update contact',
            desc='Updates a contact to HubSpot based on provided data.',
            icon='plugin',
            group=["Connectors"],
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

