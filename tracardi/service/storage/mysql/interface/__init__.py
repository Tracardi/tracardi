from tracardi.service.license import License

if License.has_license():
    import com_tracardi.storage.mysql.interface.destination as destination_dao
    import com_tracardi.storage.mysql.interface.resource as resource_dao
    import com_tracardi.storage.mysql.interface.event_source as event_source_dao
    import com_tracardi.storage.mysql.interface.event_validation as event_validation_dao
    import com_tracardi.storage.mysql.interface.event_mapping as event_mapping_dao
    import com_tracardi.storage.mysql.interface.event_to_profile_mapping as event_to_profile_dao
    import com_tracardi.storage.mysql.interface.event_reshaping as event_reshaping_dao
    import com_tracardi.storage.mysql.interface.identification_point as identification_point_dao
    import com_tracardi.storage.mysql.interface.data_compliance as data_compliance_dao
    import com_tracardi.storage.mysql.interface.consent_type as consent_type_dao
    import com_tracardi.storage.mysql.interface.deployment as deployment_dao
    import com_tracardi.storage.mysql.interface.event_redirect as event_redirect_dao
    import com_tracardi.storage.mysql.interface.workflow as workflow_dao
    import com_tracardi.storage.mysql.interface.workflow_trigger as workflow_trigger_dao
else:
    import tracardi.service.storage.mysql.interface.destination as destination_dao
    import tracardi.service.storage.mysql.interface.resource as resource_dao
    import tracardi.service.storage.mysql.interface.event_source as event_source_dao
    import tracardi.service.storage.mysql.interface.event_validation as event_validation_dao
    import tracardi.service.storage.mysql.interface.event_mapping as event_mapping_dao
    import tracardi.service.storage.mysql.interface.event_to_profile_mapping as event_to_profile_dao
    import tracardi.service.storage.mysql.interface.event_reshaping as event_reshaping_dao
    import tracardi.service.storage.mysql.interface.identification_point as identification_point_dao
    import tracardi.service.storage.mysql.interface.data_compliance as data_compliance_dao
    import tracardi.service.storage.mysql.interface.consent_type as consent_type_dao
    import tracardi.service.storage.mysql.interface.deployment as deployment_dao
    import tracardi.service.storage.mysql.interface.event_redirect as event_redirect_dao
    import tracardi.service.storage.mysql.interface.workflow as workflow_dao
    import tracardi.service.storage.mysql.interface.workflow_trigger as workflow_trigger_dao

__all__ = [
    'destination_dao',
    'resource_dao',
    'event_source_dao',
    'event_validation_dao',
    'event_mapping_dao',
    'event_to_profile_dao',
    'event_reshaping_dao',
    'identification_point_dao',
    'data_compliance_dao',
    'consent_type_dao',
    'deployment_dao',
    'event_redirect_dao',
    'workflow_dao',
    'workflow_trigger_dao'
]
