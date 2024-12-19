from typing import Tuple, Optional, List, Generator
from tracardi.domain.consent_type import ConsentType
from tracardi.service.storage.mysql.mapping.consent_type_mapping import map_to_consent_type
from tracardi.service.storage.mysql.service.consent_type_service import ConsentTypeService
from tracardi.service.storage.mysql.utils.select_result import SelectResult

cts = ConsentTypeService()


def _records(records: SelectResult) -> Tuple[List[ConsentType], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_consent_type)), records.count()


async def load_all(search: Optional[str] = None, limit: int = None, offset: int = None) -> Generator[
    ConsentType, None, None]:
    records = await cts.load_all(search, limit, offset)
    return records.map_to_objects(map_to_consent_type)


async def load(search: Optional[str] = None, limit: int = None, offset: int = None) -> Tuple[List[ConsentType], int]:
    return _records(await cts.load_all(search, limit, offset))


async def load_by_id(consent_type_id: str) -> Optional[ConsentType]:
    record = await cts.load_by_id(consent_type_id)
    if not record.exists():
        return None
    return record.map_to_object(map_to_consent_type)


async def delete_by_id(consent_type_id: str) -> Tuple[bool, Optional[ConsentType]]:
    return await cts.delete_by_id(consent_type_id)


async def insert(consent_type: ConsentType):
    return await cts.insert(consent_type)


async def load_enabled(limit: int = None, offset: int = None) -> Tuple[List[ConsentType], int]:
    return _records(await cts.load_enabled(limit, offset))
