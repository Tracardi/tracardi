from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import Resource
from tracardi.process_engine.action.v1.connectors.mautic.client import MauticClient, MauticClientException, \
    MauticClientAuthException
from tracardi.exceptions.exception import StorageException


def validate(config: dict) -> Config:
    return Config(**config)


class MauticContactByEmailFetcher(ActionRunner):

    client: MauticClient
    resource: Resource
    config: Config

    async def set_up(self, init) :
        config = validate(init)
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.resource = resource
        self.client = MauticClient(**self.resource.credentials.get_credentials(self, None))
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)

        contact_email = dot[self.config.contact_email]

        try:
            result = await self.client.fetch_contact_by_email(str(contact_email))
            return Result(port="response", value=result)

        except MauticClientAuthException:
            try:
                await self.client.update_token()

                result = await self.client.fetch_contact_by_email(str(contact_email))

                if self.debug:
                    self.resource.credentials.test = self.client.credentials
                else:
                    self.resource.credentials.production = self.client.credentials
                await storage.driver.resource.save_record(self.resource)

                return Result(port="response", value=result)

            except MauticClientAuthException as e:
                return Result(port="error", value={"error": str(e), "msg": ""})

            except StorageException as e:
                return Result(port="error", value={"error": "Plugin was unable to update credentials.", "msg": str(e)})

            except MauticClientException as e:
                return Result(port="error", value={"error": "Mautic API error", "msg": str(e)})

        except MauticClientException as e:
            return Result(port="error", value={"error": "Mautic API error", "msg": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='MauticContactByEmailFetcher',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            manual="fetch_mautic_contact_by_email_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "contact_email": None
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Mautic resource",
                                description="Please select your Mautic resource, containing your private and public "
                                            "key.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "mautic"})
                            ),
                            FormField(
                                id="contact_email",
                                name="Contact email address",
                                description="Please type in the path to email address of the contact that you want to "
                                            "fetch.",
                                component=FormComponent(type="dotPath", props={"label": "Email"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Get contact by email',
            brand='Mautic',
            desc='Fetches a profile from Mautic, based on provided email address.',
            icon='mautic',
            group=["Mautic"],
            tags=['mailing'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response from Mautic API."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
