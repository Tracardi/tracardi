from typing import Optional, List, Tuple, Generator

from tracardi.domain.identification_point import IdentificationPoint
from tracardi.service.storage.mysql.service.idetification_point_service import IdentificationPointService
from tracardi.service.storage.mysql.mapping.identification_point_mapping import map_to_identification_point
from tracardi.service.storage.mysql.utils.select_result import SelectResult

ips = IdentificationPointService()


def _records(records: SelectResult) -> Tuple[List[IdentificationPoint], int]:
    if not records.exists():
        return [], 0

    return list(records.map_to_objects(map_to_identification_point)), records.count()


async def load_all(query, limit, start) -> Tuple[List[IdentificationPoint], int]:
    result = await ips.load_all(search=query, limit=limit, offset=start)
    return _records(result)


async def load_by_id(identification_point_id: str) -> Optional[IdentificationPoint]:
    ips = IdentificationPointService()
    record = await ips.load_by_id(identification_point_id)
    if not record.exists():
        return None
    return record.map_to_object(map_to_identification_point)


async def load_by_event_type(event_type_id) -> Tuple[List[IdentificationPoint], int]:
    result = await ips.load_by_event_type(event_type_id)
    return _records(result)


async def load_enabled(limit: int) -> Generator[IdentificationPoint, None, None]:
    records = await ips.load_enabled(limit)
    return records.map_to_objects(map_to_identification_point)


# Cache

async def load_by_event_type_and_source(source_id: str, event_type_id: str) -> Generator[IdentificationPoint, None, None]:
    records = await ips.load_enabled_by_event_type_and_source(source_id, event_type_id)
    return records.map_to_objects(map_to_identification_point)


async def delete_by_id(identification_point_id: str):
    await ips.delete_by_id(identification_point_id)


async def insert(identification_point: IdentificationPoint):
    return await ips.insert(identification_point)
