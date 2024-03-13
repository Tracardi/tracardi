from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.domain import resource as resource_db
from tracardi.domain.resource import Resource
from tracardi.process_engine.action.v1.connectors.mautic.client import MauticClient, MauticClientException, \
    MauticClientAuthException
from tracardi.exceptions.exception import StorageException


def validate(config: dict) -> Config:
    return Config(**config)


class MauticContactByIDFetcher(ActionRunner):

    client: MauticClient
    resource: Resource
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.resource = resource
        self.client = MauticClient(**self.resource.credentials.get_credentials(self, None))
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)

        contact_id = dot[self.config.contact_id]

        try:
            result = await self.client.fetch_contact_by_id(str(contact_id))
            return Result(port="response", value=result)

        except MauticClientAuthException:
            try:
                await self.client.update_token()

                result = await self.client.fetch_contact_by_id(str(contact_id))

                if self.debug:
                    self.resource.credentials.test = self.client.credentials
                else:
                    self.resource.credentials.production = self.client.credentials
                await resource_db.save_record(self.resource)

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
            className='MauticContactByIDFetcher',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT + CC",
            author="Dawid Kruk",
            manual="fetch_mautic_contact_by_id_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "contact_id": None
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
                                id="contact_id",
                                name="Contact ID",
                                description="Please type in the path to ID of the contact that you want to fetch.",
                                component=FormComponent(type="dotPath", props={"label": "ID"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Get contact by ID',
            brand='Mautic',
            desc='Fetches a profile from Mautic, based on provided ID.',
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
