from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials
from tracardi.process_engine.action.v1.connectors.salesforce.marketing_cloud.client import MarketingCloudClient, \
    MarketingCloudClientException, MarketingCloudAuthException
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class DataExtensionSender(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'DataExtensionSender':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return DataExtensionSender(config, resource.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.client = MarketingCloudClient(**credentials.get_credentials(self))

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)
        self.config.mapping = traverser.reshape(self.config.mapping)

        try:
            await self.client.add_record(self.config.mapping, self.config.extension_id, self.config.update)
            return Result(port="success", value=payload)

        except MarketingCloudAuthException:
            await self.client.get_token()

            try:
                await self.client.add_record(self.config.mapping, self.config.extension_id, self.config.update)

                resource = await storage.driver.resource.load(self.config.source.id)
                if self.debug:
                    resource.credentials.test = self.client.credentials
                else:
                    resource.credentials.production = self.client.credentials

                await storage.driver.resource.save_record(resource)
                return Result(port="success", value=payload)

            except (MarketingCloudClientException, MarketingCloudAuthException) as e:
                return Result(port="error", value={"detail": str(e)})

        except Exception as e:
            return Result(port="error", value={"detail": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='DataExtensionSender',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.3',
            license="MIT",
            author="Dawid Kruk",
            init={
                "source": {
                    "id": "",
                    "name": ""
                },
                "extension_id": None,
                "update": False,
                "mapping": {}
            },
            manual="send_to_data_extension_action",
            form=Form(groups=[FormGroup(name="Salesforce Data Extension plugin", fields=[
                FormField(
                    id="source",
                    name="Marketing Cloud resource",
                    description="Select your Marketing Cloud resource, containing subdomain and client credentials.",
                    component=FormComponent(type="resource", props={"tag": "marketing_cloud"})
                ),
                FormField(
                    id="extension_id",
                    name="Data Extension ID",
                    description="Provide an ID of your data extension. You can find it in the URL copied from the name "
                                "of your extension. For more information - check documentation.",
                    component=FormComponent(type="text", props={"label": "Data Extension ID"})
                ),
                FormField(
                    id="update",
                    name="Update records",
                    description="Decide whether the plugin should update existent records, or only add new ones. ON - "
                                "modify existent data, OFF - don't modify data.",
                    component=FormComponent(type="bool", props={"label": "Update records"})
                ),
                FormField(
                    id="mapping",
                    name="Record mapping",
                    description="Provide key-value pairs, where key is the name of the column in the Data Extension, "
                                "and value is the path to the field with value for this column in added record.",
                    component=FormComponent(type="keyValueList", props={"label": "Columns"})
                )
            ])])
        ),
        metadata=MetaData(
            name='Send to Data Extension',
            desc='Sends data to Data Extension table in Salesforce Marketing Cloud, according to given mapping.',
            icon='plugin',
            group=["Salesforce"],
            brand="Salesforce",
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "success": PortDoc(desc="This port returns payload if the action was successful."),
                    "error": PortDoc(desc="This port returns optional error info if there was an error.")
                }
            )
        )
    )
