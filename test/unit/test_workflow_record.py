from datetime import datetime

from tracardi.config import tracardi
from tracardi.context import ServerContext, Context
from tracardi.domain.flow import Flow
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
        projects='Project1,Project2',
        draft=encrypt(flow),
        prod=None,
        backup=None,
        lock=True,
        deployed=True
    )

    flow_record = map_to_workflow_record(workflow_table)

    flow = Flow.from_workflow_record(flow_record, 'draft')

    assert flow.id is not None
    assert flow.timestamp is not None
    assert flow.name == "Empty"
    assert flow.wf_schema.version == str(tracardi.version)
    assert flow.flowGraph.nodes == []
    assert flow.flowGraph.edges == []
    assert flow.type == "collection"

    flow = Flow.from_workflow_record(flow_record, 'production')
    assert flow is None


def test_flow_to_workflow_table_mapping():
    with ServerContext(Context(production=True)):
        flow = Flow.new()
        flow_record = flow.get_production_workflow_record()

        table = map_to_workflow_table(flow_record)

        assert table.id == flow.id
        assert table.name == flow.name

