import logging
from typing import Optional, Tuple

from tracardi.config import tracardi
from tracardi.domain.consent_field_compliance import EventDataCompliance
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.event_data_compliance_mapping import map_to_event_data_compliance_table, \
    map_to_event_data_compliance
from tracardi.service.storage.mysql.schema.table import EventDataComplianceTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService
from tracardi.service.storage.mysql.service.table_filtering import where_tenant_and_mode_context

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class ConsentDataComplianceService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(EventDataComplianceTable, search, limit, offset)

    async def load_by_id(self, data_compliance_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(EventDataComplianceTable, primary_id=data_compliance_id)

    async def delete_by_id(self, data_compliance_id: str) -> Tuple[bool, Optional[EventDataCompliance]]:
        return await self._delete_by_id_in_deployment_mode(EventDataComplianceTable, map_to_event_data_compliance, primary_id=data_compliance_id)

    async def insert(self, consent_data_compliance: EventDataCompliance):
        return await self._replace(EventDataComplianceTable, map_to_event_data_compliance_table(consent_data_compliance))

    async def load_by_event_type(self, event_type_id: str, enabled_only: bool = True):
        if enabled_only:
            where = where_tenant_and_mode_context(
                EventDataComplianceTable,
                EventDataComplianceTable.event_type_id == event_type_id,
                EventDataComplianceTable.enabled == enabled_only
            )
        else:
            where = where_tenant_and_mode_context(
                EventDataComplianceTable,
                EventDataComplianceTable.event_type_id == event_type_id
            )

        return await self._select_in_deployment_mode(EventDataComplianceTable,
                                                     where=where,
                                                     order_by=EventDataComplianceTable.name)
