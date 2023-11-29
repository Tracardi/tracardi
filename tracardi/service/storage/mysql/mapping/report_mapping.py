from tracardi.service.storage.mysql.schema.table import ReportTable
from tracardi.domain.report import Report
from tracardi.context import get_context
from tracardi.service.storage.mysql.utils.serilizer import to_json, from_json

def map_to_report_table(report: Report) -> ReportTable:
    context = get_context()
    return ReportTable(
        id=report.id,
        name=report.name,
        description=report.description,
        tags=",".join(report.tags),
        index=report.index,
        query=to_json(report.query),
        enabled=report.enabled,

        tenant=context.tenant,
        production=context.production,
    )

def map_to_report(report_table: ReportTable) -> Report:
    return Report(
        id=report_table.id,
        name=report_table.name,
        description=report_table.description,
        tags=report_table.tags.split(','),
        index=report_table.index,
        query=from_json(report_table.query),
        enabled=report_table.enabled
    )
