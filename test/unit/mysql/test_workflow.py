from datetime import datetime

from tracardi.context import ServerContext, Context
from tracardi.domain.flow import FlowRecord
from tracardi.service.storage.mysql.mapping.workflow_mapping import map_to_workflow_table, map_to_workflow_record
from tracardi.service.storage.mysql.schema.table import WorkflowTable


def test_valid_flow_record():
    with ServerContext(Context(production=True)):

        flow_record = FlowRecord(
            id="flow_1",
            timestamp=datetime.now(),
            deploy_timestamp=datetime.now(),
            name="Flow 1",
            description="This is flow 1",
            type="collection",
            tags=["General"],
            draft={},
            lock=True,
        )

        workflow_table = map_to_workflow_table(flow_record)

        assert isinstance(workflow_table, WorkflowTable)
        assert workflow_table.id == "flow_1"
        assert workflow_table.timestamp == flow_record.timestamp
        assert workflow_table.deploy_timestamp == flow_record.deploy_timestamp
        assert workflow_table.name == "Flow 1"
        assert workflow_table.description == "This is flow 1"
        assert workflow_table.type == "collection"
        assert workflow_table.tags == "General"
        assert workflow_table.draft == {}
        assert workflow_table.lock == True
        assert workflow_table.production

def test_maps_workflow_table_to_flow_record():
        workflow_table = WorkflowTable(
            id='123',
            timestamp=datetime.now(),
            deploy_timestamp=datetime.now(),
            name='Test Workflow',
            description='This is a test workflow',
            type='collection',
            tags='Project1,Project2',
            draft={},
            lock=True,
            deployed=True
        )

        flow_record = map_to_workflow_record(workflow_table)

        assert flow_record.id == '123'
        assert flow_record.timestamp == workflow_table.timestamp
        assert flow_record.deploy_timestamp == workflow_table.deploy_timestamp
        assert flow_record.name == 'Test Workflow'
        assert flow_record.description == 'This is a test workflow'
        assert flow_record.type == 'collection'
        assert flow_record.tags == ['Project1', 'Project2']
        assert flow_record.draft == {}
        assert flow_record.lock is True
