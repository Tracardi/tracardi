from datetime import datetime

from tracardi.config import tracardi
from tracardi.context import ServerContext, Context
from tracardi.domain.flow import Flow, FlowRecord
from tracardi.service.secrets import encrypt
from tracardi.service.storage.mysql.mapping.workflow_mapping import map_to_workflow_record, map_to_workflow_table
from tracardi.service.storage.mysql.schema.table import WorkflowTable


def test_workflow_record_via_workflow_table():
    flow = Flow.new()

    assert flow.id is not None
    assert flow.timestamp is not None
    assert flow.name == "Empty"
    assert flow.wf_schema.version == str(tracardi.version)
    assert flow.flowGraph.nodes == []
    assert flow.flowGraph.edges == []
    assert flow.type == "collection"

    workflow_table = WorkflowTable(
        id='123',
        timestamp=datetime.now(),
        deploy_timestamp=datetime.now(),
        name='Test Workflow',
        description='This is a test workflow',
        type='collection',
        tags='Project1,Project2',
        draft=flow.model_dump(mode='json'),
        lock=True,
        deployed=True
    )

    flow_record = map_to_workflow_record(workflow_table)

    flow = Flow.from_workflow_record(flow_record)

    assert flow.id is not None
    assert flow.timestamp is not None
    assert flow.name == "Empty"
    assert flow.wf_schema.version == str(tracardi.version)
    assert flow.flowGraph.nodes == []
    assert flow.flowGraph.edges == []
    assert flow.type == "collection"


def test_workflow_only_from_metadata():
    flow = FlowRecord(id="1", name="test", description="", type='collection')

    # Should not fail

    assert flow.name == 'test'
    assert flow.id == '1'
    assert flow.description == ''
    assert flow.type == 'collection'