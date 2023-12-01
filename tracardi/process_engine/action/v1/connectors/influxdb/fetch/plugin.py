from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.domain import resource as resource_db
from .model.config import Config, InfluxCredentials
from influxdb_client import InfluxDBClient
from tracardi.service.plugin.domain.result import Result
from tracardi.service.notation.dict_traverser import DictTraverser


def validate(config: dict) -> Config:
    return Config(**config)


class InfluxFetcher(ActionRunner):

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

        filters = traverser.reshape(self.config.filters)
        stop = str(dot[self.config.stop])
        start = str(dot[self.config.start])

        filters = [f'filter(fn:(r) => r.{key} == "{value}")' for key, value in filters.items()]
        query = "\n |> ".join([
            fr'from(bucket:"{self.config.bucket}")',
            fr"range(start: {start}, stop: {stop})",
            *filters
        ])

        if self.config.aggregation not in (None, ""):
            query += f"\n |> {self.config.aggregation}"

        self.console.log(f"Filtering data with the following query: {query}")

        query_api = self.client.query_api()

        try:
            result = query_api.query(query, self.config.organization, {"Content-Type": "text/plain"})
            if sum((len(res.records) for res in result)) > 20:
                return Result(port="error", value={"error": "Too much records fetched from InfluxDB."})
            return Result(port="success", value=result)

        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={"error": str(e)})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='InfluxFetcher',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.2',
            license="MIT + CC",
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
                "start": "-15m",
                "stop": "0m"
            },
            form=Form(

                groups=[
                    FormGroup(
                        name="InfluxDb configuration",
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
                                description="Please type the name of your InfluxDB organization.",
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
                                            "for example _measurement) and value is the value that you want it to "
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
                                description="Type the path to lower time bound for your search. "
                                            "It can be either relative (so for example -30m), or fixed as a date.",
                                component=FormComponent(type="dotPath", props={"label": "Lower", "defaultMode": 2})
                            ),
                            FormField(
                                id="stop",
                                name="Upper time bound",
                                description="Type the path to the upper bound of your search span. As before, it "
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
            icon='influxdb',
            group=["InfluxDB"],
            tags=['database', 'analytics'],
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
