import logging
from typing import Optional, Tuple

from sqlalchemy import Integer, func

from tracardi.config import tracardi
from tracardi.domain.setting import Setting
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.setting_mapping import map_to_settings_table, map_to_setting
from tracardi.service.storage.mysql.schema.table import SettingTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class SettingService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(SettingTable, search, limit, offset)

    async def load_by_id(self, setting_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(SettingTable, primary_id=setting_id)

    async def delete_by_id(self, setting_id: str) -> Tuple[bool, Optional[Setting]]:
        return await self._delete_by_id_in_deployment_mode(SettingTable, map_to_setting,
                                                           primary_id=setting_id)

    async def insert(self, setting: Setting):
        return await self._replace(SettingTable, map_to_settings_table(setting))

    async def load_new(self) -> SelectResult:

        where = where_tenant_and_mode_context(
            SettingTable,
            func.json_extract(SettingTable.config, '$.metric.new') == True,
            # SettingTable.config['metric']['new'].cast(Boolean) == True,
            SettingTable.enabled == True
        )

        return await self._select_in_deployment_mode(
            SettingTable,
            where=where)

    async def load_by_type(self, time_based: bool) -> SelectResult:
        if time_based:
            # All metrics that limit time - are time based.

            where = where_tenant_and_mode_context(
                SettingTable,
                func.json_extract(SettingTable.config, '$.metric.span').cast(Integer) != 0,
                # SettingTable.config['metric']['span'].cast(Integer) != 0,
                SettingTable.enabled == True
            )

        else:

            where = where_tenant_and_mode_context(
                SettingTable,
                func.json_extract(SettingTable.config, '$.metric.span').cast(Integer) == 0,
                # SettingTable.config['metric']['span'].cast(Integer) == 0,
                SettingTable.enabled == True
            )

        return await self._select_in_deployment_mode(
            SettingTable,
            where=where)
