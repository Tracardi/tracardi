from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from .model.config import Config, InfluxCredentials
from tracardi.domain.resource import ResourceCredentials
from influxdb_client import InfluxDBClient
from tracardi.service.plugin.domain.result import Result
from tracardi.service.notation.dict_traverser import DictTraverser


def validate(config: dict) -> Config:
    return Config(**config)


class InfluxFetcher(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'InfluxFetcher':
        config = Config(**kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return InfluxFetcher(config, resource.credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.credentials = credentials.get_credentials(self, InfluxCredentials)
        self.client = InfluxDBClient(self.credentials.url, self.credentials.token)

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)

        self.config.filters = traverser.reshape(self.config.filters)
        self.config.stop = str(dot[self.config.stop])
        self.config.start = str(dot[self.config.start])

        self.config.filters = [f'filter(fn:(r) => r.{key} == "{value}")' for key, value in self.config.filters.items()]
        query = "\n |> ".join([
            fr'from(bucket:"{self.config.bucket}")',
            fr"range(start: {self.config.start}, stop: {self.config.stop})",
            *self.config.filters
        ])
        if self.config.aggregation not in (None, ""):
            query += f"\n |> {self.config.aggregation}"

        query_api = self.client.query_api()

        try:
            result = query_api.query(query, self.config.organization, {"Content-Type": "text/plain"})
            if sum((len(res.records) for res in result)) > 20:
                return Result(port="error", value={"error": "Too much records fetched from InfluxDB."})
            return Result(port="success", value=result)

        except Exception as e:
            return Result(port="error", value={"error": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='InfluxFetcher',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.1',
            license="MIT",
            author="Dawid Kruk",
            manual="fetch_from_influxdb_action",
            init={
                "source": {
                    "id": None,
                    "name": None
                },
                "organization": None,
                "bucket": None,
                "filters": {},
                "aggregation": None,
                "start": None,
                "stop": None
            },
            form=Form(
                name="Plugin configuration",
                groups=[
                    FormGroup(
                        fields=[
                            FormField(
                                id="source",
                                name="InfluxDB resource",
                                description="Please select your InfluxDB resource with URL and token.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "influx"})
                            ),
                            FormField(
                                id="organization",
                                name="Organization",
                                description="Please type the name of your InfluxDB organization that you want to fetch "
                                            "data from.",
                                component=FormComponent(type="text", props={"label": "Organization"})
                            ),
                            FormField(
                                id="bucket",
                                name="Bucket",
                                description="Please type the name of the bucket that you want to fetch data from.",
                                component=FormComponent(type="text", props={"label": "Bucket"})
                            ),
                            FormField(
                                id="filters",
                                name="Filters",
                                description="Please insert key-value pairs, where key is the key in InfluxDB record ("
                                            "for example _measurement) and value is the value that we want it to "
                                            "contain. Feel free to use dot paths.",
                                component=FormComponent(type="keyValueList", props={"label": "Filters"})
                            ),
                            FormField(
                                id="aggregation",
                                name="Aggregation function",
                                description='If you want, you can insert a Flux aggregation function, for example '
                                            'count(column: "_value"), or distinct().',
                                component=FormComponent(type="text", props={"label": "Aggregation"})
                            ),
                            FormField(
                                id="start",
                                name="Lower time bound",
                                description="Here type the path to lower time bound for your search. "
                                            "It can be either relative (so for example -30m), or fixed as a date.",
                                component=FormComponent(type="dotPath", props={"label": "Lower"})
                            ),
                            FormField(
                                id="stop",
                                name="Upper time bound",
                                description="Here type the path to the upper bound of your search span. As before, it "
                                            "can be either relative or fixed.",
                                component=FormComponent(type="dotPath", props={"label": "Upper"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Fetch from InfluxDB',
            desc='Gets data from provided InfluxDB resource.',
            icon='plugin',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "success": PortDoc(desc="This port return fetched data."),
                    "error": PortDoc(desc="This port gets triggered when an error occurs.")
                }
            )
        )
    )
