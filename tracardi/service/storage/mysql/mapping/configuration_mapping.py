from tracardi.domain.configuration import Configuration
from tracardi.service.storage.mysql.schema.table import ConfigurationTable
from tracardi.context import get_context

def map_to_configuration_table(configuration: Configuration) -> ConfigurationTable:
    context = get_context()
    return ConfigurationTable(
        id=configuration.id,
        timestamp=configuration.timestamp,
        name=configuration.name,
        config=configuration.config,
        enabled=configuration.enabled,
        tags=",".join(configuration.tags) if configuration.tags else "",
        description=configuration.description,
        tenant=context.tenant,
        ttl=configuration.ttl
    )

def map_to_configuration(configuration_table: ConfigurationTable) -> Configuration:
    return Configuration(
        id=configuration_table.id,
        name=configuration_table.name,
        timestamp=configuration_table.timestamp,
        config=configuration_table.config,
        enabled=configuration_table.enabled,
        description=configuration_table.description,
        tags=configuration_table.tags.split(",") if configuration_table.tags else [],
        ttl=configuration_table.ttl
    )
