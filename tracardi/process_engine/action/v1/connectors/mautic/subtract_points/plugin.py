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


class MauticPointsSubtractor(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'MauticPointsSubtractor':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return MauticPointsSubtractor(config, resource)

    def __init__(self, config: Config, resource: Resource):
        self.config = config
        self.resource = resource
        self.client = MauticClient(**self.resource.credentials.get_credentials(self, None))

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)

        self.config.contact_id = dot[self.config.contact_id]

        try:
            await self.client.subtract_points(int(self.config.contact_id), int(self.config.points))
            return Result(port="success", value=payload)

        except MauticClientAuthException:
            try:
                await self.client.update_token()

                await self.client.subtract_points(int(self.config.contact_id), int(self.config.points))

                if self.debug:
                    self.resource.credentials.test = self.client.credentials
                else:
                    self.resource.credentials.production = self.client.credentials
                await storage.driver.resource.save_record(self.resource)

                return Result(port="success", value=payload)

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
            className='MauticPointsSubtractor',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            manual="subtract_point_in_mautic_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "contact_id": None,
                "points": None
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
                                description="Please type in the path to ID of the contact that you want to subtract"
                                            " points from.",
                                component=FormComponent(type="dotPath", props={"label": "ID"})
                            ),
                            FormField(
                                id="points",
                                name="Number of points",
                                description="Please type in the number of points that you want to subtract.",
                                component=FormComponent(type="text", props={"label": "Points"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Mautic: Subtract points',
            desc='Subtracts points from a given contact in Mautic, based on provided contact ID.',
            icon='mautic',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "success": PortDoc(desc="This port returns payload if everything is OK."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
