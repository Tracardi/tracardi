from datetime import datetime
from typing import Optional
from tracardi.domain.value_threshold import ValueThreshold
from tracardi.service.storage.driver import storage


class ValueThresholdManager:

    def __init__(self, name, ttl, debug, node_id, profile_id=None):
        self.debug = debug
        self.ttl = int(ttl)
        self.name = name
        self.profile_id = profile_id
        self.node_id = "{}-{}".format(node_id, "1" if self.debug is True else "0")
        if profile_id is not None:
            self.id = "{}-{}-{}".format("1" if self.debug is True else "0", node_id, profile_id)
        else:
            self.id = "{}-{}".format("1" if self.debug is True else "0", node_id)

    async def pass_threshold(self, current_value):
        value_threshold = await self.load_last_value()
        if value_threshold is not None:
            if self.ttl > 0:
                # With timestamp
                ttl_timestamp = datetime.timestamp(value_threshold.timestamp) + self.ttl
                now = datetime.timestamp(datetime.utcnow())
                if value_threshold.last_value == current_value and now < ttl_timestamp:
                    return False
            else:
                if value_threshold.last_value == current_value:
                    return False

        await self.save_current_value(current_value)
        return True

    async def load_last_value(self) -> Optional[ValueThreshold]:
        record = await storage.driver.value_threshold.load(self.id)
        if record is not None:
            return ValueThreshold.decode(record)
        return None

    async def delete(self):
        result = await storage.driver.value_threshold.delete(self.id)
        await storage.driver.value_threshold.refresh()
        return result

    async def save_current_value(self, current_value):
        value = ValueThreshold(
            id=self.id,
            profile_id=self.profile_id,
            name=self.name,
            timestamp=datetime.utcnow(),
            ttl=self.ttl,
            last_value=current_value,
        )
        record = value.encode()
        result = await storage.driver.value_threshold.save(record)
        await storage.driver.value_threshold.refresh()
        return result
