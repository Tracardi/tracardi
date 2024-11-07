import json

from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.service.notation.dict_traverser import DictTraverser

from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from .model.config import Config
from tracardi.service.storage.elastic.interface import raw as raw_db


def validate(config: dict):
    config = Config(**config)
    return config

class WriteLocalDatabase(ActionRunner):

    config: Config

    async def set_up(self, init):
        self.config = Config(**init)

    async def run(self, payload: dict, in_edge=None) -> Result:
        
        dot = self._get_dot_accessor(payload)

        try:
            
            index=dot[self.config.index]
            documents=dot[self.config.documents]
            identifier=dot[self.config.identifier]
            
            if isinstance(documents, str):
                documents = json.loads(documents)
            
            if isinstance(documents, list) and identifier:
                documents = [{identifier: item} for item in documents]          
                
            if identifier:
                for item in documents:
                    if identifier in item:
                        item["_id"] = item[identifier]

            result = await raw_db.bulk_upsert(
                    index=index,
                    data=documents   
                )
            
            if isinstance(result, BulkInsertResult):
                result_dict = result.dict()
            
        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={
                "message": str(e)
            })

        return Result(port="result", value=result_dict)

def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className=WriteLocalDatabase.__name__,
            inputs=["payload"],
            outputs=["result", "error"],
            version='1.0.3',
            license="MIT",
            author="Matt Cameron",
            manual='write_data',
            init={
                "index": None,
                "document": None
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Elasticsearch resource",
                                description="Please select your Elasticsearch resource.",
                                component=FormComponent(type="resource", props={"label": "Resource",
                                                                                "tag": "elasticsearch"})
                            ),
                            FormField(
                                id="index",
                                name="Index",
                                description="The index for where the documents will be upserted.",
                                component=FormComponent(type="dotPath", props={
                                    "label": "Index"
                                })
                            ),
                            FormField(
                                id="documents",
                                name="Documents",
                                description="The documents to be upserted/inserted.",
                                component=FormComponent(type="dotPath", props={
                                    "label": "Documents"
                                })
                            ),
                            FormField(
                                id="identifier",
                                name="Identifier",
                                description="The primary key to be used if documents are to be upserted.",
                                component=FormComponent(type="dotPath", props={
                                    "label": "Documents"
                                })
                            ),
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Write data',
            desc='Write local Elasticsearch database',
            icon='elasticsearch',
            group=["Databases"],
            tags=['database', 'nosql', 'elastic'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "result": PortDoc(desc="This port returns result of upserting ElasticSearch instance."),
                    "error": PortDoc(desc="This port returns error if an error occurs.")
                }
            )
        )
    )
