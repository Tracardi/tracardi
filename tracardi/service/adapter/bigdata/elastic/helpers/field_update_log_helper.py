from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.elastic.driver.factory import storage_manager


async def load_field_update_log_by_type(type: str) -> StorageRecords:
    field_value_pairs = [
        ('type', type)
    ]
    return await storage_manager("field-update-log").load_by_values(field_value_pairs)
