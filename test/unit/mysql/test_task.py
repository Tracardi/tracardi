from datetime import datetime

from tracardi.context import ServerContext, Context
from tracardi.domain.task import Task
from tracardi.service.storage.mysql.mapping.task_mapping import map_to_task_table, map_to_task
from tracardi.service.storage.mysql.schema.table import TaskTable


def test_maps_task_to_task_table_with_all_fields_correctly_filled():
    context = Context(production=True, tenant="test")

    with ServerContext(context):
        # Arrange
        task = Task(
            id="123",
            name="Test Task",
            task_id="456",
            timestamp=datetime.utcnow(),
            status="pending",
            progress=0.5,
            type="import",
            params={"param1": "value1", "param2": "value2"}
        )

        expected_task_table = TaskTable(
            id="123",
            tenant="test",
            production=True,
            timestamp=task.timestamp,
            status="pending",
            name="Test Task",
            type="import",
            progress=0.5,
            task_id="456",
            params={"param1": "value1", "param2": "value2"}
        )

        # Act
        result = map_to_task_table(task)

        # Assert
        assert result.id == expected_task_table.id
        assert result.timestamp == expected_task_table.timestamp
        assert result.status == expected_task_table.status
        assert result.params == expected_task_table.params
        assert result.task_id == expected_task_table.task_id
        assert result.type == expected_task_table.type
        assert result.name == expected_task_table.name


def test_correctly_map_fields():
    task_table = TaskTable(
        id="123",
        timestamp=datetime.utcnow(),
        status="running",
        name="Test Task",
        type="import",
        progress=0.5,
        task_id="456",
        params={"param1": "value1", "param2": "value2"}
    )

    expected_task = Task(
        id="123",
        timestamp=task_table.timestamp,
        status="running",
        name="Test Task",
        type="import",
        progress=0.5,
        task_id="456",
        params={"param1": "value1", "param2": "value2"}
    )

    assert map_to_task(task_table) == expected_task
