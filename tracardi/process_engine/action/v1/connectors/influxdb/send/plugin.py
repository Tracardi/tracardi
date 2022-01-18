from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.action_runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.config import Config, InfluxCredentials
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from tracardi.service.storage.driver import storage
from tracardi.domain.resource import ResourceCredentials
from tracardi.service.notation.dict_traverser import DictTraverser


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
        self.credentials = client_credentials.get_credentials(self, InfluxCredentials)
        self.client = InfluxDBClient(self.credentials.url, self.credentials.token)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)
        self.config.fields = traverser.reshape(self.config.fields)
        self.config.tags = {str(key_tag): str(key_value) for key_tag, key_value in
                            traverser.reshape(self.config.tags).items()}

        self.config.time = dot[self.config.time] if isinstance(dot[self.config.time], (str, int, float)) else \
            str(dot[self.config.time])
        self.config.measurement = dot[self.config.measurement] if \
            isinstance(dot[self.config.measurement], (str, int, float)) else str(dot[self.config.time])

        record = {
            "measurement": self.config.measurement,
            "fields": self.config.fields,
            "tags": self.config.tags
        }
        if self.config.time not in ("None", None):
            record["time"] = self.config.time

        writer = self.client.write_api(write_options=SYNCHRONOUS)
        try:
            writer.write(
                self.config.bucket,
                self.config.organization,
                record
            )
            return Result(port="success", value=payload)
        except Exception as e:
            return Result(port="error", value=payload)


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
            manual="send_to_influx_db_action",
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "bucket": None,
                "fields": {},
                "measurement": None,
                "time": None,
                "tags": {},
                "organization": None
            },
            form=Form(
                name="Plugin configuration",
                groups=[
                    FormGroup(
                        fields=[
                            FormField(
                                id="source",
                                name="InfluxDB resource",
                                description="Please select your InfluxDB resource with token and URL.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "influx"})
                            ),
                            FormField(
                                id="bucket",
                                name="Bucket",
                                description="Please type in the name of bucket that you want to write in.",
                                component=FormComponent(type="text", props={"label": "Bucket"})
                            ),
                            FormField(
                                id="fields",
                                name="Fields",
                                description="Please map the keys to the values to send as record fields to"
                                            "InfluxDB.",
                                component=FormComponent(type="keyValueList", props={"label": "Fields"})
                            ),
                            FormField(
                                id="measurement",
                                name="Measurement value",
                                description="Please type the path to the field that will be consider as measurement for"
                                            "InfluxDB record.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="time",
                                name="Time value",
                                description="Please type the path to the field containing date, or string, or timestamp"
                                            "that will be interpreted as timestamp for your record. This parameter is "
                                            "optional.",
                                component=FormComponent(type="dotPath", props={"label": "Prefix"})
                            ),
                            FormField(
                                id="tags",
                                name="Record tags",
                                description="Please map tags for the record to values.",
                                component=FormComponent(type="keyValueList", props={"label": "Tags"})
                            ),
                            FormField(
                                id="organization",
                                name="Organization",
                                description="Please type the name of the organization that you want to use for writing.",
                                component=FormComponent(type="text", props={"label": "Organization"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Send to InfluxDB',
            desc='Sends data to InfluxDB.',
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
