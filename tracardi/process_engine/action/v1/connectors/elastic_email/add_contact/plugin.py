from datetime import datetime

import ElasticEmail
from ElasticEmail.api import contacts_api
from ElasticEmail.model.contact_payload import ContactPayload
from ElasticEmail.model.contact_status import ContactStatus

from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import Resource


def validate(config: dict) -> Config:
    return Config(**config)


class ElasticEmailContactAdder(ActionRunner):
    @staticmethod
    async def build(**kwargs) -> 'ElasticEmailContactAdder':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return ElasticEmailContactAdder(config, resource)

    def __init__(self, config: Config, resource: Resource):
        self.config = config
        self.resource = resource
        self.creds = self.resource.credentials.get_credentials(self, None)
        # self.client = ElasticEmail(**self.resource.credentials.get_credentials(self, None))

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
        configuration = ElasticEmail.Configuration()
        configuration.api_key['apikey'] = self.creds['api_key']
        # configuration.api_key_prefix['apikey'] = 'Bearer'
        contact_status = mapping.get('status')
        if contact_status:
            del mapping['status']
        list_names = mapping.get('list_names')
        if list_names:
            list_names = list_names.split(',')
            del mapping['list_names']
        contact_payload = [
            ContactPayload(
                # status=ContactStatus(contact_status or "Active"),
                email=email,
                # **mapping,
            ),
        ]
        try:
            with ElasticEmail.ApiClient(configuration) as api_client:
                api_instance = contacts_api.ContactsApi(api_client)
                if list_names:
                    # api_response = await api_instance.contacts_post(contact_payload, listnames=list_names, async_req=True)
                    api_response = api_instance.contacts_post(contact_payload, listnames=list_names)
                else:
                    api_response = api_instance.contacts_post(contact_payload)
                return Result(port="response", value=api_response)
        except Exception as e:
            return Result(port="error", value={"error": str(e), "msg": ""})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='ElasticEmailContactAdder',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.7.3',
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
                                component=FormComponent(type="dotPath", props={"label": "Email"})
                            ),
                            FormField(
                                id="additional_mapping",
                                name="Additional fields",
                                description="You can add some more fields to your contact. Just type in the alias of "
                                            "the field as key, and a path as a value for this field. This is fully "
                                            "optional. (Example: lastname: profile@pii.last_name",
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
            icon='elastic-email',
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
