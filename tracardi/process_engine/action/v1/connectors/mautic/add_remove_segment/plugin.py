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


class MauticSegmentEditor(ActionRunner):

    actions: dict
    client: MauticClient
    resource: Resource
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.resource = resource
        self.client = MauticClient(**self.resource.credentials.get_credentials(self, None))
        self.actions = {"add": self.client.add_to_segment, "remove": self.client.remove_from_segment}
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)

        contact_id = dot[self.config.contact_id]

        try:
            await self.actions[self.config.action](contact_id, self.config.segment)
            return Result(port="success", value=payload)

        except MauticClientAuthException:
            try:
                await self.client.update_token()

                await self.actions[self.config.action](contact_id, self.config.segment)

                if self.debug:
                    self.resource.credentials.test = self.client.credentials
                else:
                    self.resource.credentials.production = self.client.credentials
                await resource_db.save_record(self.resource)

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
            className='MauticSegmentEditor',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.2',
            license="MIT + CC",
            author="Dawid Kruk",
            manual="edit_segment_in_mautic_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "action": None,
                "contact_id": None,
                "segment": None
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
                                id="action",
                                name="Action",
                                description="Please define whether you want to remove given profile from given segment"
                                            ", or add it to given segment.",
                                component=FormComponent(type="select", props={"label": "Action", "items": {
                                    "add": "Add",
                                    "remove": "Remove"
                                }})
                            ),
                            FormField(
                                id="contact_id",
                                name="Contact ID",
                                description="Please type in the path to ID of the contact that you want to add to"
                                            " the segment.",
                                component=FormComponent(type="dotPath", props={"label": "ID"})
                            ),
                            FormField(
                                id="segment",
                                name="Segment ID",
                                description="Please type in the ID of the segment that you want to add or remove given "
                                            "contact from.",
                                component=FormComponent(type="text", props={"label": "Add to"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Edit segmentation',
            brand='Mautic',
            desc='Edits segmentation of given contact in Mautic, based on provided contact ID.',
            icon='mautic',
            group=["Mautic"],
            tags=['mailing'],
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
