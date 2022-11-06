from typing import Tuple

from tracardi.service.storage.indices_manager import get_indices_status


async def is_schema_ok() -> Tuple[bool, list]:

    # Missing indices

    _indices = [item async for item in get_indices_status()]
    missing_indices = [idx[1] for idx in _indices if idx[0] == 'missing_index']
    # existing_indices = [idx[1] for idx in _indices if idx[0] == 'existing_index']
    # missing_templates = [idx[1] for idx in _indices if idx[0] == 'missing_template']
    missing_aliases = [idx[1] for idx in _indices if idx[0] == 'missing_alias']
    # existing_aliases = [idx[1] for idx in _indices if idx[0] == 'existing_alias']
    # existing_templates = [idx[1] for idx in _indices if idx[0] == 'existing_template']

    is_schema_ok = not missing_indices and not missing_aliases and not missing_aliases

    return is_schema_ok, _indices