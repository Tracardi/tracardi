from datetime import datetime

from tracardi.context import ServerContext, Context
from tracardi.domain.destination import DestinationConfig
from tracardi.domain.resource import Resource, ResourceCredentials
from tracardi.service.secrets import encrypt
from tracardi.service.storage.mysql.mapping.resource_mapping import map_to_resource_table, map_to_resource
from tracardi.service.storage.mysql.schema.table import ResourceTable


def test_maps_resource_to_resource_table():
    with ServerContext(Context(production=True)):
        # Arrange
        resource = Resource(
            id="123",
            type="test",
            timestamp=datetime.utcnow(),
            name="Test Resource",
            description="This is a test resource",
            credentials=ResourceCredentials(test={"test": 1}, production={"production": 1}),
            tags=["tag1", "tag2"],
            groups=["group1", "group2"],
            icon="icon",
            destination=DestinationConfig(package="package", init={}, form={}),
            enabled=True
        )

        # Act
        result = map_to_resource_table(resource)

        # Assert
        assert result.id == "123"
        assert result.production
        assert result.type == "test"
        assert result.timestamp == resource.timestamp
        assert result.name == "Test Resource"
        assert result.description == "This is a test resource"
        assert result.credentials == encrypt(resource.credentials)
        assert result.enabled is True
        assert result.tags == "tag1,tag2"
        assert result.groups == "group1,group2"
        assert result.icon == "icon"
        assert result.destination == resource.destination.encode()


def test_all_attributes_mapped():
    dest = DestinationConfig(package="1",init={}, form={})
    resource_table = ResourceTable(
        id="123",
        tenant="test",
        production=True,
        type="test",
        timestamp=datetime.utcnow(),
        name="Test Resource",
        description="This is a test resource",
        credentials=encrypt(ResourceCredentials()),
        enabled=True,
        tags="tag1,tag2",
        groups="group1,group2",
        icon="icon",
        destination=encrypt(dest)
    )

    expected_resource = Resource(
        id="123",
        type="test",
        timestamp=resource_table.timestamp,
        name="Test Resource",
        description="This is a test resource",
        credentials=ResourceCredentials(),
        enabled=True,
        tags=["tag1", "tag2"],
        groups=["group1", "group2"],
        icon="icon",
        destination=dest
    )

    assert map_to_resource(resource_table) == expected_resource
