# from datetime import datetime
#
# from tracardi.context import Context, ServerContext
# from tracardi.domain.live_segment import WorkflowSegmentationTrigger
# from tracardi.domain.named_entity import NamedEntity
# from tracardi.service.storage.mysql.mapping.segment_trigger_mapping import map_to_workflow_segmentation_trigger, \
#     map_to_workflow_segmentation_trigger_table
# from tracardi.service.storage.mysql.schema.table import WorkflowSegmentationTriggerTable
#
#
# def test_maps_live_segment_to_segment_trigger_table_with_correct_values():
#     with ServerContext(Context(production=True)):
#         segment_trigger = WorkflowSegmentationTrigger(
#             id="123",
#             timestamp=datetime.utcnow(),
#             name="Test Segment",
#             description="This is a test segment",
#             enabled=True,
#             workflow=NamedEntity(id="456", name="Test Workflow"),
#             type="workflow",
#             operation="operation",
#             condition="condition",
#             segment="segment",
#             code="code"
#         )
#
#         # Execute
#         result = map_to_workflow_segmentation_trigger_table(segment_trigger)
#
#         # Assert
#         assert result.id == "123"
#         assert result.timestamp == segment_trigger.timestamp
#         assert result.name == "Test Segment"
#         assert result.description == "This is a test segment"
#         assert result.enabled is True
#         assert result.type == "workflow"
#         assert result.operation == "operation"
#         assert result.condition == "condition"
#         assert result.segment == "segment"
#         assert result.code == 'code'
#         assert result.workflow_id == "456"
#         assert result.workflow_name == "Test Workflow"
#         assert result.production
#
#
# def test_valid_segment_trigger_mapping():
#     segment_trigger_table = WorkflowSegmentationTriggerTable(
#         id="123",
#         timestamp=datetime.utcnow(),
#         name="Test Segment",
#         description="This is a test segment",
#         enabled=True,
#         type="segment",
#         condition="test condition",
#         operation="test operation",
#         segment="test segment",
#         code="test code",
#         workflow_id="456",
#         workflow_name="Test Workflow",
#         tenant="test",
#         production=True
#     )
#
#     expected = WorkflowSegmentationTrigger(
#         id="123",
#         name="Test Segment",
#         timestamp=segment_trigger_table.timestamp,
#         description="This is a test segment",
#         enabled=True,
#         workflow=NamedEntity(id="456", name="Test Workflow"),
#         type="segment",
#         condition="test condition",
#         operation="test operation",
#         segment="test segment",
#         code="test code"
#     )
#
#     assert map_to_workflow_segmentation_trigger(segment_trigger_table) == expected
