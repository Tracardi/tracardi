import pytest
from uuid import uuid4
from tracardi.context import ServerContext, Context
from tracardi.domain.destination import Destination, DestinationConfig, NamedEntity
from tracardi.service.destination.utils import get_destination_types
from tracardi.service.storage.mysql.service.destination_service import DestinationService

@pytest.mark.asyncio
async def test_destination_service():
    with ServerContext(Context(production=True)):
        # Initialize service
        service = DestinationService()

        # Test data setup
        destination_id = uuid4().hex
        try:
            destination_config = DestinationConfig(package="test.package", init={}, form={})
            destination_entity = NamedEntity(id="id", name="name")
            destination = Destination(
                id=destination_id,
                name="Test Destination",
                description="Test Description",
                destination=destination_config,
                enabled=True,
                tags=["test", "destination"],
                mapping={},
                condition="",
                on_profile_change_only=False,
                resource=destination_entity,
                event_type=destination_entity,
                source=destination_entity
            )

            # Insert Destination
            await service.insert(destination)

            # Load Destination by ID
            loaded_destination = await service.load_by_id(destination_id)
            assert loaded_destination.rows.id == destination_id

            # Load Event Destinations
            event_destinations = await service.load_event_destinations("id", "id")
            assert event_destinations.rows

            # Load Profile Destinations
            profile_destinations = await service.load_profile_destinations()
            assert not profile_destinations.rows

            # Get Destination Types (custom method, might require mocking or additional setup)
            destination_types = list(get_destination_types())
            assert destination_types

            # Filter Destinations
            filtered_destinations = await service.filter("Test")
            assert any(dest.id == destination_id for dest in filtered_destinations.rows)

            # Delete Destination by ID
            await service.delete_by_id(destination_id)

            # Verify Deletion
            deleted_destination = await service.load_by_id(destination_id)
            assert deleted_destination.rows is None

            destination = Destination(
                id=destination_id,
                name="Test Destination",
                description="Test Description",
                destination=destination_config,
                enabled=True,
                tags=["test", "destination"],
                mapping={},
                condition="",
                on_profile_change_only=True,
                resource=destination_entity,
                event_type=destination_entity,
                source=destination_entity
            )

            # Insert Destination
            await service.insert(destination)

            # Load Profile Destinations
            profile_destinations = await service.load_profile_destinations()
            assert profile_destinations.rows

        finally:
            await service.delete_by_id(destination_id)