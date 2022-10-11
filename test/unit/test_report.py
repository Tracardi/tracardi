from pydantic import ValidationError
from tracardi.domain.report import Report


def test_report_entities():
    for entity in ("profile", "session", "event", "entity", "improper-value-1", "improper-value-2"):
        try:
            report = Report(
                id="@test-report",
                name="test-report",
                description="Here's report description.",
                index=entity,
                query={"query": {"term": {"type": "{{type}}"}}},
                tags=["tag1", "tag2"]
            )
            assert report.index in ("profile", "session", "event", "entity")

        except ValidationError as e:
            assert entity in ("improper-value-1", "improper-value-2")
