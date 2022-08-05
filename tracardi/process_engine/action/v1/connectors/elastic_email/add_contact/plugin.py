from datetime import datetime
from multiprocessing.pool import ApplyResult

import ElasticEmail
from ElasticEmail.api import contacts_api
from ElasticEmail.model.contact_payload import ContactPayload
from ElasticEmail.model.contact_status import ContactStatus
from ElasticEmail.model.email_send import EmailSend
from asyncio import sleep

from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config, Connection
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

        configuration = ElasticEmail.Configuration()
        configuration.api_key['apikey'] = self.credentials.api_key

        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)

        email = dot[self.config.email]

        mapping = traverser.reshape(self.config.additional_mapping)
        mapping = self.parse_mapping(mapping)

        contact_other = {}
        contact_status = mapping.get('status')
        if contact_status:
            del mapping['status']

        contact_other['status'] = ContactStatus(contact_status or "Active")
        email_list_names = mapping.get('list_names')
        if email_list_names:
            email_list_names = email_list_names.split(',')
            del mapping['list_names']

        first_name = mapping.get('first_name')
        if first_name:
            del mapping['first_name']
            contact_other['first_name'] = first_name

        last_name = mapping.get('last_name')
        if last_name:
            del mapping['last_name']
            contact_other['last_name'] = last_name

        contact_payload = [
            ContactPayload(
                email=email,
                custom_fields=mapping,
                **contact_other,
            ),
        ]
        try:
            with ElasticEmail.ApiClient(configuration) as api_client:
                api_instance = contacts_api.ContactsApi(api_client)

                if email_list_names:
                    thread = api_instance.contacts_post(contact_payload, listnames=email_list_names, async_req=True)  # type: ApplyResult
                else:
                    thread = api_instance.contacts_post(contact_payload, async_req=True)  # type: ApplyResult

                # Do not block the event loop
                await sleep(0)

                # Fetch result
                api_response = thread.get()

                # todo do not know why EmailSend is checked both calls returns list of Contacts
                if isinstance(api_response, EmailSend):
                    return Result(port="response", value=api_response.to_dict())
                else:
                    return Result(port="response", value={"result": [item.to_dict() for item in api_response]})

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
                                component=FormComponent(type="dotPath", props={"label": "Email"})
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
