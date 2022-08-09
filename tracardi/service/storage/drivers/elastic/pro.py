from typing import Optional

from tracardi.domain.entity import Entity
from tracardi.domain.sign_up_data import SignUpRecord
from tracardi.domain.storage_record import StorageRecord
from tracardi.service.storage.factory import storage_manager, StorageFor


async def read_pro_service_endpoint() -> Optional[SignUpRecord]:
    return await StorageFor(Entity(id="0")).index("tracardi-pro").load(SignUpRecord)  # type: Optional[SignUpRecord]


async def save_pro_service_endpoint(sign_up_record: SignUpRecord):
    sign_up_record.id = '0'
    return await storage_manager("tracardi-pro").upsert(sign_up_record)


async def delete_pro_service_endpoint():
    return await StorageFor(Entity(id="0")).index("tracardi-pro").delete()


async def refresh():
    return await storage_manager('tracardi-pro').refresh()
