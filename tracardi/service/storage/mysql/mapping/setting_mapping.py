from tracardi.context import get_context
from tracardi.service.storage.mysql.schema.table import SettingTable
from tracardi.domain.setting import Setting


def map_to_settings_table(setting: Setting) -> SettingTable:
    context = get_context()

    return SettingTable(
        id=setting.id,
        tenant=context.tenant,
        production=context.production,
        name=setting.name,
        timestamp=setting.timestamp,
        description=setting.description or "",
        type=setting.type,
        enabled=setting.enabled,
        content=setting.content,
        config=setting.config
    )


def map_to_setting(settings_table: SettingTable) -> Setting:
    return Setting(
        id=settings_table.id,
        name=settings_table.name,
        timestamp=settings_table.timestamp,
        description=settings_table.description or "",
        type=settings_table.type,
        enabled=settings_table.enabled,
        content=settings_table.content,
        config=settings_table.config,
        production=settings_table.production,
        running=settings_table.running
    )


