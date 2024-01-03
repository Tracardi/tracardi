import logging

from tracardi.config import tracardi
from tracardi.domain.setting import Setting

from tracardi.context import Context, ServerContext
from tracardi.domain.bridge import Bridge
from tracardi.domain.consent_field_compliance import EventDataCompliance
from tracardi.domain.consent_type import ConsentType
from tracardi.domain.destination import Destination
from tracardi.domain.event_redirect import EventRedirect
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
from tracardi.domain.event_source import EventSource
from tracardi.domain.event_to_profile import EventToProfile
from tracardi.domain.event_type_metadata import EventTypeMetadata
from tracardi.domain.event_validator import EventValidator
from tracardi.domain.flow import FlowRecord
from tracardi.domain.identification_point import IdentificationPoint
from tracardi.domain.import_config import ImportConfig
from tracardi.domain.live_segment import WorkflowSegmentationTrigger
from tracardi.domain.report import Report
from tracardi.domain.resource import Resource, ResourceRecord
from tracardi.domain.rule import Rule
from tracardi.domain.segment import Segment
from tracardi.domain.task import Task
from tracardi.domain.user import User
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.bridge_mapping import map_to_bridge_table
from tracardi.service.storage.mysql.mapping.consent_type_mapping import map_to_consent_type_table
from tracardi.service.storage.mysql.mapping.destination_mapping import map_to_destination_table
from tracardi.service.storage.mysql.mapping.event_data_compliance_mapping import map_to_event_data_compliance_table
from tracardi.service.storage.mysql.mapping.event_redirect_mapping import map_to_event_redirect_table
from tracardi.service.storage.mysql.mapping.event_reshaping_mapping import map_to_event_reshaping_table
from tracardi.service.storage.mysql.mapping.event_source_mapping import map_to_event_source_table
from tracardi.service.storage.mysql.mapping.event_to_event_mapping import map_to_event_mapping_table
from tracardi.service.storage.mysql.mapping.event_to_profile_mapping import map_to_event_to_profile_table
from tracardi.service.storage.mysql.mapping.event_validation_mapping import map_to_event_validation_table
from tracardi.service.storage.mysql.mapping.identification_point_mapping import map_to_identification_point
from tracardi.service.storage.mysql.mapping.import_mapping import map_to_import_config_table
from tracardi.service.storage.mysql.mapping.report_mapping import map_to_report_table
from tracardi.service.storage.mysql.mapping.resource_mapping import map_to_resource_table
from tracardi.service.storage.mysql.mapping.segment_mapping import map_to_segment_table
from tracardi.service.storage.mysql.mapping.segment_trigger_mapping import map_to_workflow_segmentation_trigger_table
from tracardi.service.storage.mysql.mapping.setting_mapping import map_to_settings_table
from tracardi.service.storage.mysql.mapping.task_mapping import map_to_task_table
from tracardi.service.storage.mysql.mapping.user_mapping import map_to_user_table
from tracardi.service.storage.mysql.mapping.workflow_mapping import map_to_workflow_table
from tracardi.service.storage.mysql.mapping.workflow_trigger_mapping import map_to_workflow_trigger_table
from tracardi.service.storage.mysql.schema.table import BridgeTable, ConsentTypeTable, SegmentTable, \
    IdentificationPointTable, EventMappingTable, EventSourceTable, EventDataComplianceTable, EventReshapingTable, \
    TaskTable, WorkflowSegmentationTriggerTable, UserTable, DestinationTable, EventRedirectTable, ReportTable, \
    EventToProfileMappingTable, WorkflowTriggerTable, ResourceTable, WorkflowTable, ImportTable, EventValidationTable, \
    SettingTable
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.worker.domain.migration_schema import MigrationSchema
from tracardi.worker.misc.update_progress import update_progress
from tracardi.worker.misc.add_task import add_task
from tracardi.worker.service.worker.migration_workers.utils.client import ElasticClient


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)

def resource_converter(resource_record: ResourceRecord) -> Resource:
    return resource_record.decode()

class_mapping = {
    "bridge": (Bridge, BridgeTable, map_to_bridge_table, None),
    "consent-type": (ConsentType, ConsentTypeTable, map_to_consent_type_table, None),
    "segment": (Segment, SegmentTable, map_to_segment_table, None),
    "identification-point": (IdentificationPoint, IdentificationPointTable, map_to_identification_point, None),
    # "events-tags": (EventTypeMetadata, EventMappingTable, map_to_event_mapping_table, None),  # todo check
    "event-source": (EventSource, EventSourceTable, map_to_event_source_table, None),
    "consent-data-compliance": (EventDataCompliance, EventDataComplianceTable, map_to_event_data_compliance_table, None),
    "event-reshaping": (EventReshapingSchema, EventReshapingTable, map_to_event_reshaping_table, None),
    # "tracardi-pro": (None, TracardiProTable, None, None), # todo check
    "task": (Task, TaskTable, map_to_task_table, None),
    "live-segment": (
        WorkflowSegmentationTrigger, WorkflowSegmentationTriggerTable, map_to_workflow_segmentation_trigger_table, None),
    "event-management": (EventTypeMetadata, EventMappingTable, map_to_event_mapping_table, None),
    "user": (User, UserTable, map_to_user_table, None),
    "destination": (Destination, DestinationTable, map_to_destination_table, None),
    "event-redirect": (EventRedirect, EventRedirectTable, map_to_event_redirect_table, None),
    # "content": (Content, ContentTable, map_to_content, None),
    "report": (Report, ReportTable, map_to_report_table, None),
    "event_to_profile": (EventToProfile, EventToProfileMappingTable, map_to_event_to_profile_table, None),
    "rule": (Rule, WorkflowTriggerTable, map_to_workflow_trigger_table, None),
    "resource": (ResourceRecord, ResourceTable, map_to_resource_table, resource_converter),
    "flow": (FlowRecord, WorkflowTable, map_to_workflow_table, None),
    "import": (ImportConfig, ImportTable, map_to_import_config_table, None),
    "event-validation": (EventValidator, EventValidationTable, map_to_event_validation_table, None),
    # "version": (None, VersionTable, None, None),
    "setting": (Setting, SettingTable, map_to_settings_table, None),
}


async def copy_to_mysql(celery_job, schema: MigrationSchema, elastic_host: str, context: Context):
    if schema.copy_index.multi is True:
        raise ValueError('Multi index can not be copied to mysql.')

    with ServerContext(context):
        await add_task(
            f"Migration of \"{schema.copy_index.from_index}\" to mysql table \"{schema.copy_index.to_index}\"",
            celery_job,
            schema.model_dump()
        )

        storage_class = schema.params['mysql']
        if storage_class not in class_mapping:
            logger.error(f'Could not find class {storage_class}')
            return


        domain_type, object_table, domain_object_mapping_to_table, converter = class_mapping[storage_class]

        chunk = 100
        moved_records = 0

        with ElasticClient(hosts=[elastic_host]) as client:
            while records_to_move := client.load_records(
                    index=schema.copy_index.from_index,
                    start=moved_records,
                    size=chunk
            ):
                update_progress(celery_job, 0, doc_count := client.count(schema.copy_index.from_index))

                for number, record in enumerate(records_to_move):  # Type: int,StorageRecord

                    try:
                        domain_object = record.to_entity(domain_type, set_metadata=False)

                        if converter is not None:
                            domain_object = converter(domain_object)

                        table_data = domain_object_mapping_to_table(domain_object)

                        print(domain_type, table_data)
                    except Exception as e:
                        print(domain_type, record)
                        exit()

                    ts = TableService()
                    print('xxx', await ts._replace(object_table, table_data))

                    # Update progress
                    update_progress(celery_job, moved_records + number + 1, doc_count)

                moved_records += chunk

        update_progress(celery_job, 100)
