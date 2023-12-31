from tracardi.context import get_context
from tracardi.domain.flow import FlowRecord
from tracardi.domain.flow_meta_data import FlowMetaData
from tracardi.service.storage.mysql.schema.table import WorkflowTable


def map_to_workflow_table(flow_record: FlowRecord) -> WorkflowTable:

    context = get_context()

    return WorkflowTable(
        id=flow_record.id,
        timestamp=flow_record.timestamp,
        deploy_timestamp=flow_record.deploy_timestamp,
        name=flow_record.name,
        description=flow_record.description,
        type=flow_record.type,
        projects=",".join(flow_record.projects) if flow_record.projects else "",

        draft=flow_record.draft.encode(),
        prod=flow_record.production.encode(),
        backup=flow_record.backup.encode(),

        lock=flow_record.lock,
        deployed=flow_record.deployed,

        tenant = context.tenant,
        production = context.production

    )

# Mapping from SQLAlchemy Table to Domain Object
def map_to_workflow_record(workflow_table: WorkflowTable) -> FlowRecord:
    return FlowRecord(
        id=workflow_table.id,
        timestamp=workflow_table.timestamp,
        deploy_timestamp=workflow_table.deploy_timestamp,
        name=workflow_table.name,
        description=workflow_table.description,
        type=workflow_table.type,
        projects=workflow_table.projects.split(",") if workflow_table.projects else [],
        draft=workflow_table.draft.decode(),
        production=workflow_table.prod.decode(),
        backup=workflow_table.backup.decode(),
        lock=workflow_table.lock,
        deployed=workflow_table.deployed
    )


def map_to_workflow_record_meta(workflow_table: WorkflowTable) -> FlowMetaData:
    return FlowMetaData(
        id=workflow_table.id,
        name=workflow_table.name,
        description=workflow_table.description,
        type=workflow_table.type,
        projects=workflow_table.projects.split(",") if workflow_table.projects else []
    )
