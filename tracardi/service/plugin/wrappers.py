from tracardi.context import get_context
from tracardi.service.plugin.domain.result import Result
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis_client import RedisClient
from tracardi.service.tracking.cache.profile_cache import load_profile_cache, save_profile_cache
from tracardi.service.tracking.cache.session_cache import load_session_cache, save_session_cache
from tracardi.service.tracking.locking import GlobalMutexLock
from tracardi.service.utils.getters import get_entity_id

_redis = RedisClient()


def lock_for_profile_update(func):
    async def wrapper(self, *args, **kwargs):

        # Lock profile for changes

        async with GlobalMutexLock(
                get_entity_id(self.profile),
                'profile',
                namespace=Collection.lock_tracker,
                redis=_redis
        ):
            # Refresh profile

            _profile = load_profile_cache(self.profile.id, get_context())

            if not _profile:
                if self.debug:
                    _profile = self.profile
                else:
                    message = f"Could not load profile id={self.profile.id} in run method of {type(self)}"
                    self.console.error(message)
                    return Result(port="error", value={"message": message})

            self.profile.replace(_profile)

            result = await func(self, *args, **kwargs)

            save_profile_cache(self.profile)

            return result

    return wrapper


def lock_for_session_update(func):
    async def wrapper(self, *args, **kwargs):
        _redis = RedisClient()

        # Lock session for changes

        async with GlobalMutexLock(
                get_entity_id(self.session),
                'session',
                namespace=Collection.lock_tracker,
                redis=_redis
        ):
            # Refresh session
            if self.debug:
                _session = self.session
            else:
                _session = load_session_cache(self.session.id, get_context())

            if not _session:
                message = f"Could not load session id={self.session.id} in run method of {type(self)}"
                self.console.error(message)
                return Result(port="error", value={"message": message})

            self.session.replace(_session)
            result = await func(self, *args, **kwargs)
            save_session_cache(self.session)

            return result

    return wrapper
