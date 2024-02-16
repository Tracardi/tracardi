from typing import Optional, Tuple

from tracardi.domain.report import Report
from tracardi.service.storage.mysql.mapping.report_mapping import map_to_report_table, map_to_report
from tracardi.service.storage.mysql.schema.table import ReportTable
from tracardi.service.storage.mysql.utils.select_result import SelectResult
from tracardi.service.storage.mysql.service.table_service import TableService


class ReportService(TableService):

    async def load_all(self, search: str = None, limit: int = None, offset: int = None) -> SelectResult:
        return await self._load_all_in_deployment_mode(ReportTable, search, limit, offset)

    async def load_by_id(self, report_id: str) -> SelectResult:
        return await self._load_by_id_in_deployment_mode(ReportTable, primary_id=report_id)

    async def delete_by_id(self, report_id: str) -> Tuple[bool, Optional[Report]]:
        return await self._delete_by_id_in_deployment_mode(ReportTable, map_to_report,
                                                           primary_id=report_id)

    async def insert(self, report: Report):
        return await self._replace(ReportTable, map_to_report_table(report))

