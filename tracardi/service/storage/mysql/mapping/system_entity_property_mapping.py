from tracardi.context import get_context
from tracardi.domain.system_entity_property import SystemEntityProperty
from tracardi.service.storage.mysql.schema.table import SystemEntityPropertyTable


def map_to_system_entity_property_table(system_entity_property: SystemEntityProperty) -> SystemEntityPropertyTable:
    context = get_context()
    return SystemEntityPropertyTable(
        id=system_entity_property.id,
        entity=system_entity_property.entity,
        property=system_entity_property.property,
        type=system_entity_property.type,
        default=system_entity_property.default,
        # Assumes the default can be directly mapped, includes handling for None
        optional=system_entity_property.optional,
        converter=system_entity_property.converter,
        # Assumes converter can be directly mapped, includes handling for None
        masked=system_entity_property.masked,  # Used to mask displayed value
        group=system_entity_property.group,  # Defines a group of properties
        tenant=context.tenant
    )


def map_to_system_entity_property(system_entity_property_table: SystemEntityPropertyTable) -> SystemEntityProperty:
    return SystemEntityProperty(
        id=system_entity_property_table.id,
        entity=system_entity_property_table.entity,
        property=system_entity_property_table.property,
        type=system_entity_property_table.type,
        default=system_entity_property_table.default,  # Properly handles the case if default is None
        optional=system_entity_property_table.optional,
        converter=system_entity_property_table.converter,  # Properly handles the case if converter is None
        masked=system_entity_property_table.masked,  # Used to mask displayed value
        group=system_entity_property_table.group # Defines a group of properties
    )
