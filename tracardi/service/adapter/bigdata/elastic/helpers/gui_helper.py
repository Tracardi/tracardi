from typing import List

from tracardi.domain.storage_record import StorageRecords
from tracardi.service.storage.elastic.driver.factory import storage_manager


async def load_profiles_by_segments(segments: List[str], condition: str = 'must') -> StorageRecords:
    """
    Requires all segments
    """
    return await storage_manager('profile').load_by_values(
        field_value_pairs=[('segments', segment) for segment in segments],
        condition=condition
    )