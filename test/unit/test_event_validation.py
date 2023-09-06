import pytest

from tracardi.domain.storage_record import StorageRecords
from tracardi.service.tracking.event_validation import get_event_validation_result


@pytest.mark.asyncio
async def test_validate_event_with_single_validation_schema():
    # Create a mock event
    event = {
        "properties": {
            "test": "string"
        }
    }

    # Create a mock validation schema
    validation_schema = StorageRecords()
    validation_schema.set_data(
        records=[
            {'_index': '08x.01506.tracardi-event-validation',
             '_type': '_doc',
             '_id': '8fe9f084-2027-4329-8a5b-ab3096ff3a9f',
             '_score': 0.5753642,
             '_source': {
                 'id': '8fe9f084-2027-4329-8a5b-ab3096ff3a9f',
                 'name': 'pageVIew validator',
                 'event_type': 'page-view',
                 'description': '',
                 'tags': [],
                 'validation': {
                     'json_schema': {
                         'event@properties.test': {
                             'type': 'string'
                         }
                     },
                     'condition': None},
                 'enabled': True}}
        ],
        total=1
    )

    # Call the function under test
    result = await get_event_validation_result(event, validation_schema)

    # Assert the result
    assert result == (False, None)
