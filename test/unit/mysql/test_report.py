from tracardi.context import Context, ServerContext
from tracardi.domain.report import Report
from tracardi.service.storage.mysql.mapping.report_mapping import map_to_report_table, map_to_report
from tracardi.service.storage.mysql.schema.table import ReportTable


def test_same_fields():
    context = Context(
        production=True,
        tenant="test_tenant"
    )

    with ServerContext(context):
        report = Report(
            id="123",
            name="Test Report",
            description="This is a test report",
            tags=["Tag1", "Tag2"],
            index="profile",
            query={"field": "value"},
            enabled=True
        )



        expected_report_table = ReportTable(
            id="123",
            name="Test Report",
            description="This is a test report",
            tags='Tag1,Tag2',
            index="profile",
            query={"field": "value"},
            enabled=True,
            tenant="test_tenant",
            production=True
        )

        converted_table = map_to_report_table(report)

        assert converted_table.id == expected_report_table.id
        assert converted_table.name == expected_report_table.name
        assert converted_table.description == expected_report_table.description
        assert converted_table.tags == expected_report_table.tags
        assert converted_table.query == expected_report_table.query
        assert converted_table.enabled == expected_report_table.enabled
        assert converted_table.production

def test_correct_mapping():
        report_table = ReportTable(
            id="123",
            name="Test Report",
            description="This is a test report",
            tags="Tag1,Tag2",
            index="profile",
            query={"param1": "{{param1}}", "param2": "{{param2}}"},
            enabled=True,
            tenant="test",
            production=True
        )

        expected_report = Report(
            id="123",
            name="Test Report",
            description="This is a test report",
            tags=["Tag1", "Tag2"],
            index="profile",
            query={"param1": "{{param1}}", "param2": "{{param2}}"},
            enabled=True
        )

        assert map_to_report(report_table) == expected_report