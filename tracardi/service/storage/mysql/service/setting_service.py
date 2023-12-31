import logging

from sqlalchemy import Boolean, Integer, func

from tracardi.config import tracardi
from tracardi.domain.setting import Setting
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.setting_mapping import map_to_settings_table
from tracardi.service.storage.mysql.schema.table import SettingTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService, where_tenant_context

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class SettingService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        where = None
        if search:
            where = where_tenant_context(
                SettingTable,
                SettingTable.name.like(f'%{search}%')
            )

        return await self._select_query(SettingTable,
                                        where=where,
                                        order_by=SettingTable.name,
                                        limit=limit,
                                        offset=offset)

    async def load_by_id(self, setting_id: str) -> SelectResult:
        return await self._load_by_id(SettingTable, primary_id=setting_id)

    async def delete_by_id(self, setting_id: str) -> str:
        return await self._delete_by_id(SettingTable, primary_id=setting_id)

    async def insert(self, setting: Setting):
        return await self._replace(SettingTable, map_to_settings_table(setting))

    async def load_new(self) -> SelectResult:

        where = where_tenant_context(
            SettingTable,
            func.json_extract(SettingTable.config, '$.metric.new') == True,
            # SettingTable.config['metric']['new'].cast(Boolean) == True,
            SettingTable.enabled == True
        )

        return await self._select_query(
            SettingTable,
            where=where)

    async def load_by_type(self, time_based: bool) -> SelectResult:
        if time_based:
            # All metrics that limit time - are time based.

            where = where_tenant_context(
                SettingTable,
                func.json_extract(SettingTable.config, '$.metric.span').cast(Integer) != 0,
                # SettingTable.config['metric']['span'].cast(Integer) != 0,
                SettingTable.enabled == True
            )

        else:

            where = where_tenant_context(
                SettingTable,
                func.json_extract(SettingTable.config, '$.metric.span').cast(Integer) == 0,
                # SettingTable.config['metric']['span'].cast(Integer) == 0,
                SettingTable.enabled == True
            )

        return await self._select_query(
            SettingTable,
            where=where)
