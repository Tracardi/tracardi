from tracardi.service.utils.date import now_in_utc
from typing import Optional
from tracardi.domain.value_threshold import ValueThreshold
from tracardi.service.storage.redis.collections import Collection
from tracardi.service.storage.redis.driver.redis_client import RedisClient

redis = RedisClient()


class ValueThresholdManager:

    def __init__(self, name, ttl, debug, node_id, profile_id=None):
        self.debug = debug
        self.ttl = int(ttl)
        self.name = name
        self.profile_id = profile_id

        debug = "1" if self.debug is True else "0"

        self.node_id = f"{debug}-{node_id}"
        if profile_id is not None:
            self.id = f"{debug}-{node_id}-{profile_id}"
        else:
            self.id = f"{debug}-{node_id}"

    @staticmethod
    def _get_key(key):
        return f"{Collection.value_threshold}{key}"

    async def pass_threshold(self, current_value):
        value = await self.load_last_value()

        if value is None or value.ttl != self.ttl or value.last_value != current_value:
            await self.save_current_value(current_value)

        if value is None:
            return True

        if value.last_value == current_value:
            return False
        return True

    async def load_last_value(self) -> Optional[ValueThreshold]:
        record = redis.get(self._get_key(self.id))
        if record is not None:
            return ValueThreshold.decode(record)
        return None

    async def delete(self):
        return redis.delete(self._get_key(self.id))

    async def save_current_value(self, current_value):
        value = ValueThreshold(
            id=self.id,
            profile_id=self.profile_id,
            name=self.name,
            timestamp=now_in_utc(),
            ttl=self.ttl,
            last_value=current_value,
        )
        record = value.encode()
        kwargs = {}
        if self.ttl > 0:
            kwargs['ex'] = self.ttl
        return redis.set(self._get_key(self.id), record, **kwargs)
