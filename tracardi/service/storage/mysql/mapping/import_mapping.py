from typing import Optional

from tracardi.context import get_context
from tracardi.domain.import_config import ImportConfig
from tracardi.service.storage.mysql.schema.table import ImportTable
from tracardi.domain.named_entity import NamedEntity

def map_to_import_config_table(import_config: ImportConfig) -> ImportTable:
    context = get_context()
    return ImportTable(
        id=import_config.id,
        tenant=context.tenant,
        production=context.production,
        name=import_config.name,
        description=import_config.description or "",
        module=import_config.module,
        config=import_config.config,
        enabled=import_config.enabled,
        transitional=False,
        api_url=import_config.api_url,
        event_source_id=import_config.event_source.id,
        event_source_name=import_config.event_source.name,
        event_type=import_config.event_type
    )

def map_to_import_config(import_table: Optional[ImportTable]) -> Optional[ImportConfig]:

    if not import_table:
        return None

    return ImportConfig(
        id=import_table.id,
        name=import_table.name,
        description=import_table.description or "",
        module=import_table.module,
        config=import_table.config,
        enabled=import_table.enabled,
        api_url=import_table.api_url,
        event_source=NamedEntity(id=import_table.event_source_id, name=import_table.event_source_name),
        event_type=import_table.event_type
    )
