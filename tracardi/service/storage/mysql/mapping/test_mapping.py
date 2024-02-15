from tracardi.context import get_context
from tracardi.service.storage.mysql.schema.table import TestTable
from tracardi.domain.test import Test
from tracardi.domain.named_entity import NamedEntity
from tracardi.service.utils.date import now_in_utc

def map_to_test_table(test: Test) -> TestTable:
    context = get_context()
    return TestTable(
        id=test.id,
        timestamp=test.timestamp or now_in_utc(),
        name=test.name,
        event_source_id=test.event_source.id,
        event_source_name=test.event_source.name,
        event_type_id=test.event_type.id,
        event_type_name=test.event_type.name,
        profile_id=test.profile_id,
        session_id=test.session_id,
        asynchronous=test.asynchronous,
        properties=test.properties or {},  # Ensure default dict if None
        context=test.context or {},  # Ensure default dict if None
        tenant=context.tenant
    )

def map_to_test(test_table: TestTable) -> Test:
    return Test(
        id=test_table.id,
        name=test_table.name,
        timestamp=test_table.timestamp,
        event_source=NamedEntity(id=test_table.event_source_id, name=test_table.event_source_name),
        event_type=NamedEntity(id=test_table.event_type_id, name=test_table.event_type_name),
        profile_id=test_table.profile_id,
        session_id=test_table.session_id,
        asynchronous=test_table.asynchronous,
        properties=test_table.properties,
        context=test_table.context
    )
