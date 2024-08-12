from tracardi.service.license import License, LICENSE
from tracardi.service.setup.mappings.object_to_table.event import event_properties_to_column_mapping
from tracardi.service.setup.mappings.object_to_table.profile import profile_properties_to_column_mapping
from tracardi.service.setup.mappings.object_to_table.session import session_properties_to_column_mapping
from tracardi.service.setup.mappings.tables.event import default_event_table_columns
from tracardi.service.setup.mappings.tables.profile import default_profile_table_columns
from tracardi.service.setup.mappings.tables.session import default_session_table_columns
from tracardi.service.setup.setup_bridges import os_default_bridges
from tracardi.service.storage.mysql.service.bridge_service import BridgeService
from tracardi.service.storage.mysql.service.system_entity_properties_service import SystemEntityPropertiesService
from tracardi.service.storage.mysql.service.system_entity_property_to_column_mapping_service import \
    SystemEntityPropertyToColumnMapping
from tracardi.service.storage.mysql.service.system_entity_table_column_service import SystemEntityTableColumnService

if License.has_license() or True:
    from com_tracardi.db.bootstrap.default_bridges import commercial_default_bridges
    from com_tracardi.service.setup.mappings.objects.event import default_event_properties
    from com_tracardi.service.setup.mappings.objects.session import default_session_properties
    from com_tracardi.service.setup.mappings.objects.profile import default_profile_properties


async def bootstrap_table_content():
    await BridgeService.bootstrap(default_bridges=os_default_bridges)
    if License.has_service(LICENSE):
        await BridgeService.bootstrap(default_bridges=commercial_default_bridges)

    # Default object properties
    await SystemEntityPropertiesService.bootstrap(
        default_profile_properties + default_event_properties + default_session_properties
    )

    # Default object storage columns
    await SystemEntityTableColumnService.bootstrap(
        default_profile_table_columns + default_event_table_columns + default_session_table_columns
    )

    # Default object properties to columns mapping
    await SystemEntityPropertyToColumnMapping.bootstrap(
        profile_properties_to_column_mapping + event_properties_to_column_mapping + session_properties_to_column_mapping
    )
