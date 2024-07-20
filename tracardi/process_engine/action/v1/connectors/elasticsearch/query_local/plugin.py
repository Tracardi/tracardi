import json

from tracardi.service.notation.dict_traverser import DictTraverser

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.config import Config
from tracardi.service.storage.elastic.interface import raw as raw_db


def validate(config: dict):
    config = Config(**config)

    # Try parsing JSON just for validation purposes
    try:
        json.loads(config.query)
    except json.JSONDecodeError as e:
        raise ValueError(str(e))

    return config


class QueryLocalDatabase(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = Config(**init)

    async def run(self, payload: dict, in_edge=None) -> Result:

        try:
            query = json.loads(self.config.query)
            dot = self._get_dot_accessor(payload)
            reshaper = DictTraverser(dot)
            query = reshaper.reshape(query)

            if 'size' not in query:
                query["size"] = 20

            if query["size"] > 50:
                self.console.warning("Fetching more then 50 records may impact the GUI performance.")

            if self.config.log:
                self.console.log(f"Executed query {query}")

            result = await raw_db.query_by_index(
                index=self.config.index,
                query=query
            )

            if self.config.log:
                self.console.log(f"Query result {result}")

        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={
                "message": str(e)
            })

        return Result(port="result", value=result.dict())


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=QueryLocalDatabase.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version='0.8.0',
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual='query_data',
            init={
                "index": None,
                "query": "{\"query\":{\"match_all\":{}}}",
                "log": False
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Configuration",
                        fields=[
                            FormField(
                                id="index",
                                name="Elasticsearch index",
                                description="Please select Elasticsearch index you want to search.",
                                component=FormComponent(type="select", props={
                                    "label": "Index",
                                    "items": {
                                        "profile": "Profile",
                                        "event": "Event",
                                        "session": "Session"
                                    }
                                })
                            ),
                            FormField(
                                id="query",
                                name="Query",
                                description="Please provide Elasticsearch DSL query.",
                                component=FormComponent(type="json", props={"label": "DSL query"})
                            ),

                            FormField(
                                id="log",
                                name="Log query",
                                description="Switch logging query body. Please disable when tests are finished.",
                                component=FormComponent(type="bool", props={"label": "Log query"})
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Query data',
            desc='Query local Elasticsearch database',
            icon='elasticsearch',
            group=["Databases"],
            tags=['database', 'nosql', 'elastic'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This port returns result of querying ElasticSearch instance."),
                    "error": PortDoc(desc="This port returns error if one occurs, or if received result contains more "
                                          "than 20 records.")
                }
            )
        )
    )
