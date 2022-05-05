from .batch_runner import BatchRunner
from pydantic import BaseModel
from tracardi.service.plugin.domain.register import Form, FormGroup, FormField, FormComponent


class MySQLBatchConfig(BaseModel):
    table_name: str
    batch: int
    event_type: str


class MySQLBatch(BatchRunner):

    form = Form(groups=[FormGroup(name="MySQL config", fields=[
        FormField(
            name="Table name",
            id="table_name",
            description="Provide a name of the table that you want to fetch data from.",
            component=FormComponent(type="text", props={"label": "Table name"})
        ),
        FormField(
            name="Batch",
            id="batch",
            description="Provide a number of records that you want to fetch from given MySQL table.",
            component=FormComponent(type="text", props={"label": "Batch"})
        ),
        FormField(
            name="Event type",
            id="event_type",
            description="Provide type of the event that you want to be triggered for every record when fetched. This "
                        "event will contain all columns with their values, attached in its properties.",
            component=FormComponent(type="text", props={"label": "Event type"})
        )
    ])])

    async def run(self, config: dict):
        self.config = MySQLBatchConfig(**config)
        
