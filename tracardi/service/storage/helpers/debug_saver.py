from tracardi.domain.value_object.bulk_insert_result import BulkInsertResult
from tracardi.domain.record.event_debug_record import EventDebugRecord
from tracardi.service.storage.factory import StorageForBulk


async def save_debug_info(debug_info_by_event_type_and_rule_name) -> BulkInsertResult:
    records = []
    for debug_info_record in EventDebugRecord.encode(
            debug_info_by_event_type_and_rule_name):  # type: EventDebugRecord
        records.append(debug_info_record)
    # Save in debug index
    return await StorageForBulk(records).index("debug-info").save(replace_id=False)
