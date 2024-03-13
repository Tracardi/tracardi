# from tracardi.domain.named_entity import NamedEntity
# from tracardi.context import get_context
# from tracardi.domain.live_segment import WorkflowSegmentationTrigger
# from tracardi.service.storage.mysql.schema.table import WorkflowSegmentationTriggerTable
#
#
# def map_to_workflow_segmentation_trigger_table(workflow_segmentation_trigger: WorkflowSegmentationTrigger) -> WorkflowSegmentationTriggerTable:
#     context = get_context()
#     return WorkflowSegmentationTriggerTable(
#         id=workflow_segmentation_trigger.id,
#         tenant=context.tenant,
#         production=context.production,
#         timestamp=workflow_segmentation_trigger.timestamp,
#         name=workflow_segmentation_trigger.name,
#         description=workflow_segmentation_trigger.description or "",  # Add default value if description not available
#         enabled=workflow_segmentation_trigger.enabled,
#         type=workflow_segmentation_trigger.type or "workflow",
#         condition=workflow_segmentation_trigger.condition,
#         operation=workflow_segmentation_trigger.operation,
#         segment=workflow_segmentation_trigger.segment,
#         code=workflow_segmentation_trigger.code,
#         workflow_id=workflow_segmentation_trigger.workflow.id,
#         workflow_name=workflow_segmentation_trigger.workflow.name
#     )
#
#
# def map_to_workflow_segmentation_trigger(workflow_segmentation_trigger_table: WorkflowSegmentationTriggerTable) -> WorkflowSegmentationTrigger:
#     return WorkflowSegmentationTrigger(
#         id=workflow_segmentation_trigger_table.id,
#         name=workflow_segmentation_trigger_table.name,
#         timestamp=workflow_segmentation_trigger_table.timestamp,
#         description=workflow_segmentation_trigger_table.description or "",
#         enabled=workflow_segmentation_trigger_table.enabled,
#         workflow=NamedEntity(id=workflow_segmentation_trigger_table.workflow_id, name=workflow_segmentation_trigger_table.workflow_name),
#         type=workflow_segmentation_trigger_table.type or "workflow",
#         condition=workflow_segmentation_trigger_table.condition,
#         operation=workflow_segmentation_trigger_table.operation,
#         segment=workflow_segmentation_trigger_table.segment,
#         code=workflow_segmentation_trigger_table.code,
#
#         running=workflow_segmentation_trigger_table.running,
#         production=workflow_segmentation_trigger_table.production
#
#     )
