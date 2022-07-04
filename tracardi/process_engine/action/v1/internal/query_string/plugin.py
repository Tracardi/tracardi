from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config
from tracardi.service.storage.factory import storage_manager
from tracardi.service.plugin.domain.result import Result
from elasticsearch import ElasticsearchException
from tracardi.service.notation.dot_template import DotTemplate
from pytimeparse import parse as parse_time


def validate(config: dict) -> Config:
    return Config(**config)


class CountRecordsAction(ActionRunner):

    def __init__(self, **kwargs):
        self.config = Config(**kwargs)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        template = DotTemplate()
        query = template.render(self.config.query, dot)

        try:

            time_span = parse_time(self.config.time_range)

            result = await storage_manager(self.config.index).storage.count_by_query_string(
                query,
                f"{time_span}s" if time_span < 0 else ""
            )

        except ElasticsearchException as e:
            return Result(port="error", value={"error": str(e)})

        return Result(port="result", value={"numberOfRecords": result})


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='CountRecordsAction',
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            manual="count_by_query_string_action",
            init={
                "index": None,
                "time_range": None,
                "query": ""
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="index",
                                name="Index",
                                description="Please select the index that you want to search for matches.",
                                component=FormComponent(type="select", props={"label": "Index", "items": {
                                    "event": "Event",
                                    "profile": "Profile",
                                    "session": "Session"
                                }})
                            ),
                            FormField(
                                id="time_range",
                                name="Time range",
                                description="Please define the time range from now that you want to search within "
                                            "(e.g. -30d).",
                                component=FormComponent(type="text", props={"label": "Time range"})
                            ),
                            FormField(
                                id="query",
                                name="Query string",
                                description="Please provide a query string that will match records to be counted. "
                                            "(e.g. type:\"page-view\"). You can use dot template as well.",
                                component=FormComponent(type="textarea", props={"label": "Query"})
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Count records',
            desc='Counts event, profile, or session records.Records can be filtered by query sting.',
            icon='plugin',
            group=["Stats"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This port returns number of records."),
                    "error": PortDoc(desc="This port returns error info if something goes wrong.")
                }
            )
        )
    )
