from tracardi.service.singleton import Singleton
from tracardi.service.storage.redis_client import RedisClient
from tracardi.domain.event_payload_validator import EventTypeManager
from typing import Optional
import json
import logging
from tracardi.config import tracardi
from tracardi.exceptions.log_handler import log_handler


logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)
logger.addHandler(log_handler)


class EventManagerCache(metaclass=Singleton):

    def __init__(self):
        self._client = RedisClient()

    def upsert_item(self, item: EventTypeManager) -> None:
        self._client.client.set(
            name=f"EVENT-TYPE-MANAGER-{item.event_type}",
            value=json.dumps(item.dict()),
            ex=15 * 60
        )
        logger.info(msg=f"Updated cache for event type metadata of type {item.event_type}")

    def delete_item(self, event_type: str) -> None:
        self._client.client.delete(f"EVENT-TYPE-MANAGER-{event_type}")
        logger.info(msg=f"Deleted cache of event type metadata of type {event_type}")

    def get_item(self, event_type: str) -> Optional[EventTypeManager]:
        data = self._client.client.get(f"EVENT-TYPE-MANAGER-{event_type}")
        return data if data is None else EventTypeManager(**json.loads(data))
