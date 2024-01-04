from typing import Tuple
from tracardi.domain.import_config import ImportConfig
from tracardi.domain.resources.elastic_resource_config import ElasticResourceConfig
from tracardi.worker.misc.task_progress import task_create
from .importer import Importer
from pydantic import field_validator, BaseModel
from tracardi.service.plugin.domain.register import Form, FormGroup, FormField, FormComponent
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.domain import resource as resource_db
from tracardi.service.plugin.plugin_endpoint import PluginEndpoint
from tracardi.worker.worker import run_elastic_import_job
from ...context import get_context


class ElasticIndexImportConfig(BaseModel):
    source: NamedEntity
    index: NamedEntity
    batch: int

    @field_validator("source", "index")
    @classmethod
    def validate_named_entities(cls, value):
        if not value.id:
            raise ValueError("This field cannot be empty.")
        return value


class Endpoint(PluginEndpoint):

    @staticmethod
    async def fetch_indices(config: dict):
        config = ElasticResourceConfig(**config)
        return await config.get_indices()


class ElasticIndexImporter(Importer):
    config_model = ElasticIndexImportConfig

    init = {
        "source": {"name": "", "id": ""},
        "index": {"name": "", "id": ""},
        "batch": 100,
    }

    form = Form(groups=[FormGroup(
        fields=[
            FormField(
                name="Elastic resource",
                id="source",
                description="Select Elasticsearch resource you want to connect to. Resource must have database credentials defined.",
                component=FormComponent(type="resource", props={"tag": "elasticsearch"})
            ),
            FormField(
                name="Index name",
                id="index",
                description="Select index that you want to fetch data from.",
                component=FormComponent(type="autocomplete", props={
                    "label": "Index",
                    "endpoint": {
                        "url": Endpoint.url(__name__, "fetch_indices"),
                        "method": "post"
                    }
                })
            ),
            FormField(
                name="Batch",
                id="batch",
                description="System will not import the whole data at once. It will break the whole data set into small batches. "
                            "Type a number of records that will be processed in one batch.",
                component=FormComponent(type="text", props={"label": "Batch"})
            )
        ])])

    async def run(self, task_name, import_config: ImportConfig):

        config = ElasticIndexImportConfig(**import_config.config)
        resource = await resource_db.load(config.source.id)
        credentials = resource.credentials.test if self.debug is True else resource.credentials.production

        # Run via huey

        run_elastic_import_job(
            task_name,
            import_config.model_dump(mode='json'),
            credentials,
            get_context()
        )
