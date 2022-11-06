from tracardi.service.singleton import Singleton
from tracardi.service.storage.redis_client import RedisClient
from tracardi.domain.event_reshaping_schema import EventReshapingSchema
import json
import logging
from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler
from typing import List


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventReshapeSchemaCache(metaclass=Singleton):

    def __init__(self):
        self._client = RedisClient()

    def upsert_item(self, item: EventReshapingSchema) -> None:
        self._client.client.set(
            name=f"EVENT-RESHAPING-SCHEMA-{item.event_type}-{item.id}",
            value=json.dumps(item.dict()),
            ex=15 * 60
        )
        logger.info(msg=f"Updated cache for event reshaping schema of type {item.event_type} with ID of {item.id}")

    def delete_item(self, id: str, event_type: str) -> None:
        self._client.client.delete(f"EVENT-RESHAPING-SCHEMA-{event_type}-{id}")
        logger.info(msg=f"Deleted cache of event reshaping schema of type {event_type} with ID of {id}")

    def get_items(self, event_type: str) -> List[EventReshapingSchema]:
        keys = self._client.client.keys(f"EVENT-RESHAPING-SCHEMA-{event_type}-*")
        data = []
        for key in keys:
            result = self._client.client.get(key)
            if result:
                data.append(EventReshapingSchema(**json.loads(result)))

        return data
