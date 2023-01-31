from typing import Tuple

from tracardi.service.storage.indices_manager import get_indices_status


def get_missing(indices, type) -> list:
    return [idx[1] for idx in indices if idx[0] == type]


async def is_schema_ok() -> Tuple[bool, list]:
    # Missing indices

    _indices = [item async for item in get_indices_status()]
    missing_indices = get_missing(_indices, type='missing_index')
    missing_aliases = get_missing(_indices, type='missing_alias')

    is_schema_ok = not missing_indices and not missing_aliases

    return is_schema_ok, _indices
