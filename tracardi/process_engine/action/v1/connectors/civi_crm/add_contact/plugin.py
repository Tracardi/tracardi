from tracardi.domain.resource_config import ResourceConfig
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormField, \
    FormGroup, FormComponent
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
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


class Endpoint(PluginEndpoint):

    @staticmethod
    async def get_custom_fields(config: dict) -> list:
        config = ResourceConfig(**config)
        resource = await storage.driver.resource.load(config.source.id)
        client = CiviCRMClient(**resource.credentials.production)
        return await client.get_custom_fields()


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
            # manual="add_civi_crm_contact_action",
            init={
                "source": {
                    "id": "",
                    "name": ""
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
                                description="Select CiviCRM resource.",
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
                                component=FormComponent(
                                    type="keyValueList",
                                    props={
                                        "defaultValueSource": "event",
                                        "endpoint": {
                                            "url": Endpoint.url(__name__, "get_custom_fields"),
                                            "method": "post"
                                        },
                                        "availableValues": [
                                            {"name": name, "id": key}
                                            for name, key in {
                                                "ID": "id",
                                                "Contact ID": "contact_id",
                                                "Contact subtype": "contact_sub_type",
                                                "Sorted name": "sort_name",
                                                "Display name": "display_name",
                                                "Do not email": "do_not_email",
                                                "Do not phone": "do_not_phone",
                                                "Do not mail": "do_not_mail",
                                                "Do not SMS": "do_not_sms",
                                                "Do not trade": "do_not_trade",
                                                "No bulk emails": "is_opt_out",
                                                "Legal identifier": "legal_identifier",
                                                "External identifier": "external_identifier",
                                                "Nickname": "nick_name",
                                                "Legal name": "legal_name",
                                                "Image URL": "image_URL",
                                                "Preferred communication method": "preferred_communication_method",
                                                "Preferred language": "preferred_language",
                                                "Preferred mail format": "preferred_mail_format",
                                                "First name": "first_name",
                                                "Middle name": "middle_name",
                                                "Last name": "last_name",
                                                "Prefix ID": "prefix_id",
                                                "Suffix ID": "suffix_id",
                                                "Formal title": "format_title",
                                                "Communication style ID": "communication_style_id",
                                                "Job title": "job_title",
                                                "Gender ID": "gender_id",
                                                "Birth date": "birth_date",
                                                "Is deceased": "is_deceased",
                                                "Deceased date": "deceased_date",
                                                "Household name": "household_name",
                                                "Organization name": "organization_name",
                                                "Sic code": "sic_code",
                                                "Is deleted": "contact_is_deleted",
                                                "Current employer": "current_employer",
                                                "Address ID": "address_id",
                                                "Street address": "street_address",
                                                "Supplemental address 1": "supplemental_address_1",
                                                "Supplemental address 2": "supplemental_address_2",
                                                "Supplemental address 3": "supplemental_address_3",
                                                "City": "city",
                                                "Postal code suffix": "postal_code_suffix",
                                                "Postal code": "postal_code",
                                                "Geo code 1": "geo_code_1",
                                                "Geo code 2": "geo_code_2",
                                                "State province ID": "state_province_id",
                                                "Country ID": "country_id",
                                                "Phone ID": "phone_id",
                                                "Phone type ID": "phone_type_id",
                                                "Phone": "phone",
                                                "Email ID": "email_id",
                                                "Email": "email",
                                                "Primary email on hold": "on_hold",
                                                "Instant messenger": "im",
                                                "Instant messenger ID": "im_id",
                                                "Phone provider ID": "provider_id",
                                                "World region ID": "worldregion_id",
                                                "World region": "world_region",
                                                "Languages": "languages",
                                                "Individual prefix": "individual_prefix",
                                                "Individual suffix": "individual_suffix",
                                                "Communication style": "communication_style",
                                                "Gender": "gender",
                                                "State province name": "state_province_name",
                                                "State province": "state_province",
                                                "Country": "country"
                                            }.items()
                                        ]
                                    }
                                )
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Add contact',
            desc='Adds new contact in CiviCRM.',
            brand='CiviCRM',
            icon='civicrm',
            group=["Civi CRM"],
            tags=['crm', 'marketing'],
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
