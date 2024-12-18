from tracardi.service.storage.mysql.schema.table import DestinationTable, EventDataComplianceTable, ConsentTypeTable, \
    IdentificationPointTable, EventToProfileMappingTable, ResourceTable, EventValidationTable, EventMappingTable, \
    EventReshapingTable, EventSourceTable, EventRedirectTable, WorkflowTable, WorkflowTriggerTable

EVENT_SOURCE_TAG = ('tracardi', EventSourceTable.__tablename__)
EVENT_RESHAPING_TAG = ('tracardi', EventReshapingTable.__tablename__)
EVENT_MAPPING_TAG = ('tracardi', EventMappingTable.__tablename__)
EVENT_VALIDATION_TAG = ('tracardi',EventValidationTable.__tablename__)
DESTINATION_TAG = ('tracardi', DestinationTable.__tablename__)
RESOURCE_TAG = ('tracardi', ResourceTable.__tablename__)
PROFILE_MAPPING_TAG = ('tracardi', EventToProfileMappingTable.__tablename__)
IDENTIFICATION_POINT_TAG = ('tracardi', IdentificationPointTable.__tablename__)
DATA_COMPLIANCE_TAG = ('tracardi', EventDataComplianceTable.__tablename__)
CONSENT_TYPE_TAG = ('tracardi', ConsentTypeTable.__tablename__)
REDIRECT_TAG = ('tracardi', EventRedirectTable.__tablename__)
WORKFLOW_TAG = ('tracardi', WorkflowTable.__tablename__)
WORKFLOW_TRIGGER_TAG = ('tracardi', WorkflowTriggerTable.__tablename__)

DEPLOYMENT_TAG = lambda table: ('tracardi', table)
