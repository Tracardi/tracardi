import logging

from tracardi.config import tracardi
from tracardi.domain.report import Report
from tracardi.exceptions.log_handler import log_handler
from tracardi.service.storage.mysql.mapping.report_mapping import map_to_report_table
from tracardi.service.storage.mysql.schema.table import ReportTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService, where_tenant_context

logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class ReportService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        where = None
        if search:
            where = where_tenant_context(
                ReportTable,
                ReportTable.name.like(f'%{search}%')
            )

        return await self._select_query(ReportTable,
                                        where=where,
                                        order_by=ReportTable.name,
                                        limit=limit,
                                        offset=offset)

    async def load_by_id(self, plugin_id: str) -> SelectResult:
        return await self._load_by_id(ReportTable, primary_id=plugin_id)

    async def delete_by_id(self, report_id: str) -> str:
        return await self._delete_by_id(ReportTable, primary_id=report_id)

    async def insert(self, report: Report):
        return await self._replace(ReportTable, map_to_report_table(report))

