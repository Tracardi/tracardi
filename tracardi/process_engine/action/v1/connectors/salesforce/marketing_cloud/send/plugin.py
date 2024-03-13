from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.domain import resource as resource_db
from tracardi.process_engine.action.v1.connectors.salesforce.marketing_cloud.client import MarketingCloudClient, \
    MarketingCloudClientException, MarketingCloudAuthException
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Config:
    return Config(**config)


class DataExtensionSender(ActionRunner):

    client: MarketingCloudClient
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.client = MarketingCloudClient(**resource.credentials.get_credentials(self))
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)
        mapping = traverser.reshape(self.config.mapping)

        try:
            await self.client.add_record(mapping, self.config.extension_id, self.config.update)
            return Result(port="success", value=payload)

        except MarketingCloudAuthException:
            await self.client.get_token()

            try:
                await self.client.add_record(mapping, self.config.extension_id, self.config.update)

                resource = await resource_db.load(self.config.source.id)
                if self.debug:
                    resource.credentials.test = self.client.credentials
                else:
                    resource.credentials.production = self.client.credentials

                await resource_db.save_record(resource)
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
            license="MIT + CC",
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
                    component=FormComponent(type="resource", props={"tag": "salesforce"})
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
            icon='salesforce',
            group=["Salesforce"],
            brand="Salesforce",
            tags=['crm'],
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
