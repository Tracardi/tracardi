from datetime import datetime
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.config import Config, InfluxCredentials
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from tracardi.service.domain import resource as resource_db
from tracardi.service.notation.dict_traverser import DictTraverser
from dateutil.parser import parse, ParserError


def validate(config: dict) -> Config:
    return Config(**config)


class InfluxSender(ActionRunner):

    client: InfluxDBClient
    credentials: InfluxCredentials
    config: Config

    async def set_up(self, init):
        config = Config(**init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, InfluxCredentials)
        self.client = InfluxDBClient(self.credentials.url, self.credentials.token)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)

        self.config.fields = traverser.reshape(self.config.fields)
        self.config.tags = {str(key_tag): str(key_value) for key_tag, key_value in
                            traverser.reshape(self.config.tags).items()}

        try:
            if self.config.time is None or self.config.time == "":
                time_data = None
            elif isinstance(self.config.time, str):
                time_data = dot[self.config.time]
                if isinstance(time_data, datetime):
                    time_data = time_data.isoformat()
                else:
                    time_data = parse(time_data).isoformat()  # will throw error if invalid string
            else:
                raise ValueError(f"Incorrect time type. Expected date as string, got {self.config.time}.")
        except KeyError:
            self.console.warning(f"Defined time value {self.config.time} does not exist. Time value set to now.")
            time_data = None
        except ParserError:
            self.console.error(f"Defined time value {self.config.time} is not a date. Time value set to now.")
            time_data = None

        record = {
            "measurement": self.config.measurement,
            "fields": self.config.fields,
            "tags": self.config.tags
        }

        if time_data is not None:
            record["time"] = time_data

        self.console.log("Record {} for bucket {} in organisation {}".format(record, self.config.bucket,
                                                                             self.config.organization))

        writer = self.client.write_api(write_options=SYNCHRONOUS)
        try:
            writer.write(
                self.config.bucket,
                self.config.organization,
                record
            )
            return Result(port="success", value=payload)
        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='InfluxSender',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.2',
            license="MIT + CC",
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
                groups=[
                    FormGroup(
                        name="Influxdb configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="InfluxDB resource",
                                description="Please select InfluxDB resource.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "influxdb"})
                            ),
                            FormField(
                                id="organization",
                                name="Organization",
                                description="Organization is a workspace for your data. Please type the name of the "
                                            "organization that you want to use for writing. When using cloud InfluxDB "
                                            "it is usually your login e-mail.",
                                component=FormComponent(type="text", props={"label": "Organization"})
                            ),
                            FormField(
                                id="bucket",
                                name="Bucket",
                                description="A bucket is a named location where time series data is stored. Please type "
                                            "in the name of bucket that you want the data to be stored.",
                                component=FormComponent(type="text", props={"label": "Bucket"})
                            ),
                            FormField(
                                id="measurement",
                                name="Measurement name",
                                description="Please type then name of the measurement, e.g. Purchase orders.",
                                component=FormComponent(type="text", props={"label": "Measurement name"})
                            ),
                            FormField(
                                id="fields",
                                name="Fields and values",
                                description="Fields are keys and values. It is the name and value of the measure. "
                                            "You can send more then one value. Value can be retrieved via path to value in"
                                            "tracardi, eg. profile@stats.visists",
                                component=FormComponent(type="keyValueList", props={"label": "Fields"})
                            ),
                            FormField(
                                id="time",
                                name="Time",
                                description="Please type date or the path to the field containing date. "
                                            "It will be become as timestamp for your record. This parameter is "
                                            "optional. Invalid data of date format will be ignored and date time will "
                                            "be set to the moment of the execution.",
                                component=FormComponent(type="dotPath", props={"label": "Time"})
                            ),
                            FormField(
                                id="tags",
                                name="Record tags",
                                description="Tags are additional data used for grouping values. They consist of key and "
                                            "value. Key is a name of the tag while value is a grouping value.",
                                component=FormComponent(type="keyValueList", props={"label": "Tags"})
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Send to InfluxDB',
            desc='Sends data to InfluxDB.',
            icon='influxdb',
            group=["InfluxDB"],
            tags=['database', 'analytics'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "success": PortDoc(desc="This port returns input payload if everything went OK."),
                    "error": PortDoc(desc="This port returns input payload if an error occurred.")
                }
            )
        )
    )
