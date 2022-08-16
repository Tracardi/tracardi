from tracardi.domain.report import Report
from tracardi.service.storage.driver import storage
from tracardi.service.storage.factory import storage_manager
from tracardi.domain.report import QueryBuildingError


class ReportManagerException(Exception):
    pass


class ReportManager:

    @staticmethod
    async def build(report_id: str) -> 'ReportManager':
        report = await storage.driver.report.load(report_id)
        if report is None:
            raise ReportManagerException(f"Report with ID `{report_id}` does not exist.")

        return ReportManager(report)

    def __init__(self, report: Report):
        self.report = report

    def get_expected_fields(self):
        return self.report.expected_query_params

    async def get_report(self, params: dict) -> dict:
        built_query = self.report.get_built_query(**params)
        return await storage_manager(self.report.index).query(built_query)
