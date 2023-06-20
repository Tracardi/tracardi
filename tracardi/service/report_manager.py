from tracardi.domain.report import Report
from tracardi.service.storage.driver.elastic import raw as raw_db
from tracardi.service.storage.driver.elastic import report as report_db


class ReportManagerException(Exception):
    pass


class ReportManager:

    @staticmethod
    async def build(report_id: str) -> 'ReportManager':
        report = await report_db.load(report_id)
        if report is None:
            raise ReportManagerException(f"Report with ID `{report_id}` does not exist.")

        return ReportManager(report)

    def __init__(self, report: Report):
        self.report = report

    def get_expected_fields(self):
        return self.report.expected_query_params

    async def get_report(self, params: dict) -> dict:
        built_query = self.report.get_built_query(**params)
        result = await raw_db.query_by_index(self.report.index, built_query)
        aggregations = result.aggregations()
        result = result.dict()
        if aggregations is not None:
            result["aggregations"] = aggregations

        return result
