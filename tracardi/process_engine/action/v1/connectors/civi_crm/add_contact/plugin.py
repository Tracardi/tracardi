from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormField, \
    FormGroup, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from .model.config import Config
from tracardi.process_engine.action.v1.connectors.civi_crm.client import CiviCRMClient, CiviCRMClientException
from tracardi.domain.resource import ResourceCredentials
from tracardi.service.plugin.domain.result import Result
from tracardi.service.notation.dict_traverser import DictTraverser


def validate(config: dict) -> Config:
    return Config(**config)


class AddCiviContactAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'AddCiviContactAction':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return AddCiviContactAction(config, resource.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.client = CiviCRMClient(**credentials.get_credentials(self))

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)
        self.config.fields = traverser.reshape(self.config.fields)

        try:
            result = await self.client.add_contact(
                data={
                    "contact_type": self.config.contact_type,
                    **{field: self.config.fields[field] for field in self.config.fields if self.config.fields[field]
                       is not None}
                }
            )
            return Result(port="success", value=result)

        except CiviCRMClientException as e:
            return Result(port="error", value={"detail": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='AddCiviContactAction',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.3',
            license="MIT",
            author="Dawid Kruk",
            #manual="add_civi_crm_contact_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "contact_type": "Individual",
                "fields": {}
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="CiviCRM add contact",
                        fields=[
                            FormField(
                                id="source",
                                name="CiviCRM resource",
                                description="Select your CiviCRM resource containing your site key, API key and API "
                                            "URL.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "civi_crm"})
                            ),
                            FormField(
                                id="contact_type",
                                name="Contact type",
                                description="Select the type of contact that you want to add.",
                                component=FormComponent(type="select", props={"label": "Contact type", "items": {
                                    "Individual": "Individual",
                                    "Organization": "Organization",
                                    "Household": "Household"
                                }})
                            ),
                            FormField(
                                id="fields",
                                name="Fields",
                                description="Enter key-value pairs, where key is the name of CiviCRM contact field, and"
                                            " value is the path to this field's value. Remember that every contact type"
                                            " has different mandatory fields: organization_name for Organization, "
                                            "household_name for Household, and one of first_name, last_name, email, "
                                            "display_name for Individual. You can also update a contact, by setting id"
                                            " key as contact's id. If it's null, then new contact will be created.",
                                component=FormComponent(type="keyValueList")
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Add contact to CiviCRM',
            desc='Adds new contact in CiviCRM according to given configuration.',
            icon='civicrm',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "success": PortDoc(desc="This port returns response from CiviCRM if the action was successful."),
                    "error": PortDoc(desc="This port returns additional error information if an error occurred.")
                }
            )
        )
    )
