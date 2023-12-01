from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.domain import resource as resource_db
from tracardi.domain.resource import Resource
from tracardi.process_engine.action.v1.connectors.mautic.client import MauticClient, MauticClientException, \
    MauticClientAuthException
from datetime import datetime
from tracardi.exceptions.exception import StorageException
from tracardi.service.notation.dict_traverser import DictTraverser


def validate(config: dict) -> Config:
    return Config(**config)


class MauticContactAdder(ActionRunner):

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

    @staticmethod
    def parse_mapping(mapping):
        for key, value in mapping.items():

            if isinstance(value, list):
                if key == "tags":
                    mapping[key] = ",".join(value)

                else:
                    mapping[key] = "|".join(value)

            elif isinstance(value, datetime):
                mapping[key] = str(value)
        return mapping

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)

        email = dot[self.config.email]

        mapping = traverser.reshape(self.config.additional_mapping)
        mapping = self.parse_mapping(mapping)

        try:
            result = await self.client.add_contact(
                email=email,
                overwrite_with_blank=self.config.overwrite_with_blank,
                **mapping
            )
            return Result(port="response", value=result)

        except MauticClientAuthException:
            try:
                await self.client.update_token()

                result = await self.client.add_contact(
                    email=email,
                    overwrite_with_blank=self.config.overwrite_with_blank,
                    **mapping
                )

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
            className='MauticContactAdder',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT + CC",
            author="Dawid Kruk",
            manual="add_mautic_contact_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "email": None,
                "additional_mapping": {},
                "overwrite_with_blank": False
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
                                id="email",
                                name="Email address",
                                description="Please type in the path to the email address for your new contact.",
                                component=FormComponent(type="dotPath", props={"label": "Email"})
                            ),
                            FormField(
                                id="additional_mapping",
                                name="Additional fields",
                                description="You can add some more fields to your contact. Just type in the alias of "
                                            "the field as key, and a path as a value for this field. This is fully "
                                            "optional. (Example: surname: profile@pii.surname",
                                component=FormComponent(type="keyValueList", props={"label": "Fields"})
                            ),
                            FormField(
                                id="overwrite_with_blank",
                                name="Overwrite with blank",
                                description="If you do not mention any field in config, you can overwrite it with empty"
                                            " value. Otherwise it will be skipped while adding contact.",
                                component=FormComponent(type="bool", props={"label": "Set to empty"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Add contact',
            brand='Mautic',
            desc='Adds a new contact to Mautic based on provided data.',
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
