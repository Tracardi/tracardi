import os

from tracardi.service.cluster.settings import GlobalSettings
from tracardi.service.utils.environment import get_env_as_bool

global_settings = GlobalSettings()
_default_save_logs = get_env_as_bool('SAVE_LOGS', 'yes')
_default_enable_visit_ended = get_env_as_bool('ENABLE_VISIT_ENDED', 'no')


async def is_save_logs_on() -> bool:
    return await global_settings.get("SAVE_LOGS", _default_save_logs) is True


async def is_visit_ended_on() -> bool:
    return await global_settings.get("ENABLE_VISIT_ENDED", _default_enable_visit_ended) is True
