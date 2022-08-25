from datetime import datetime
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config, Connection
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import Resource
from ..client import ElasticEmailClient


def validate(config: dict) -> Config:
    return Config(**config)


class ElasticEmailContactAdder(ActionRunner):

    credentials: Connection
    config: Config

    async def set_up(self, init):
        config = Config(init)
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=Connection)  # type: Connection

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
        mapping = traverser.reshape(self.config.additional_mapping)
        mapping = self.parse_mapping(mapping)

        contact_data = {"email": dot[self.config.email]}
        if mapping.get("list_name"):
            contact_data["listName"] = mapping["list_name"]
            del mapping["list_names"]
        if mapping.get("first_name"):
            contact_data["firstName"] = mapping["first_name"]
            del mapping["first_name"]
        if mapping.get("last_name"):
            contact_data["lastName"] = mapping["last_name"]
            del mapping["last_name"]
        if mapping:
            contact_data["field"] = mapping
        try:
            result = await self.client.add_contact(
                contact_data, field=mapping
            )
            return Result(port="response", value=result)
        except Exception as e:
            return Result(port="error", value={"message": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ElasticEmailContactAdder',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.2',
            license="MIT",
            author="Ben Ullrich",
            manual="elastic_email_contact_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "email": None,
                "additional_mapping": {},
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Elastic Email resource",
                                description="Please select your Elastic Email resource, containing your api key",
                                component=FormComponent(type="resource",
                                    props={"label": "Resource", "tag": "elastic-email"})
                            ),
                            FormField(
                                id="email",
                                name="Email address",
                                description="Please type in the path to the email address for your new contact.",
                                component=FormComponent(type="dotPath", props={"label": "Email",
                                                                               "defaultSourceValue": "profile",
                                                                               "defaultPathValue": "pii.email"
                                                                               })
                            ),
                            FormField(
                                id="additional_mapping",
                                name="Additional fields",
                                description="You can add some more fields to your contact. Just type in the alias of "
                                            "the field as key, and a path as a value for this field. This is fully "
                                            "optional. (Example: last_name: profile@pii.last_name",
                                component=FormComponent(type="keyValueList", props={"label": "Fields"})
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Add contact',
            brand='Elastic Email',
            desc='Adds a new contact to Elastic Email based on provided data.',
            icon='email',
            group=["Elastic Email"],
            tags=['mailing'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns response from Elastic Email API."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
