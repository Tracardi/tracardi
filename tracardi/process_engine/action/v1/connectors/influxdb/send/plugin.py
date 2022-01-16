from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc
from tracardi.service.plugin.action_runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.config import Config, InfluxCredentials
from influxdb import InfluxDBClient
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials
import json


def validate(config: dict) -> Config:
    return Config(**config)


class InfluxSender(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'InfluxSender':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return InfluxSender(config, resource.credentials)

    def __init__(self, config: Config, client_credentials: ResourceCredentials):
        self.config = config
        credentials = client_credentials.get_credentials(self, InfluxCredentials)
        self.client = InfluxDBClient(credentials.host, credentials.port, credentials.username, credentials.password)

    async def run(self, payload):
        self.client.switch_database(self.config.database)
        response = self.client.write(
            data=json.dumps(payload)
        )
        if not response:
            return Result(port="error", value=payload)
        return Result(port="success", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='InfluxSender',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.1',
            license="MIT",
            author="Dawid Kruk",
            # TODO MANUAL
            # TODO FORM
            # TODO ADD NEW RESOURCE TYPE
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "database": None
            }
        ),
        metadata=MetaData(
            name='Send to local InfluxDB',
            desc='Sends payload to local InfluxDB',
            type='flowNode',
            icon='plugin',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "success": PortDoc(desc="This port returns given payload if everything went OK."),
                    "error": PortDoc(desc="This port returns given payload if an error occurred.")
                }
            )
        )
    )
