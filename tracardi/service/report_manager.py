from tracardi.domain.report import Report
from tracardi.service.storage.elastic.interface import raw as raw_db
from tracardi.service.storage.mysql.mapping.report_mapping import map_to_report
from tracardi.service.storage.mysql.service.report_service import ReportService


class ReportManagerException(Exception):
    pass


class ReportManager:

    @staticmethod
    async def build(report_id: str) -> 'ReportManager':
        rs = ReportService()
        record = await rs.load_by_id(report_id)

        if not record.exists():
            raise ReportManagerException(f"Report with ID `{report_id}` does not exist.")

        report = record.map_to_object(map_to_report)
        # report = await report_db.load(report_id)

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
