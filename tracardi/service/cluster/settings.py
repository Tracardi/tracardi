from json import JSONDecodeError

import random

import json
import redis

from pydantic.v1 import ValidationError
from typing import Any

from pydantic import BaseModel

from time import sleep

import asyncio

from tracardi.context import Context, ServerContext
from tracardi.domain import ExtraInfo
from tracardi.domain.configuration import Configuration
from tracardi.exceptions.log_handler import get_logger
from tracardi.service.singleton import Singleton
from tracardi.service.storage.mysql.mapping.configuration_mapping import map_to_configuration
from tracardi.service.storage.mysql.service.configuration_service import ConfigurationService
from tracardi.service.storage.redis.driver.redis_client import RedisClient
from tracardi.service.utils.date import now_in_utc
from threading import Thread


logger = get_logger(__name__)

class ValueMessage(BaseModel):
    key: str
    value: Any


class GlobalSettingsBroadcaster(metaclass=Singleton):

    def __init__(self):
        self.redis = RedisClient()
        self.subscriber = self.redis.pubsub()
        self.channel = 'global-broadcaster'
        self.settings = GlobalSettings()

    def _listen_for_messages(self):
        while True:
            try:
                self.subscriber.subscribe(self.channel)
                for message in self.subscriber.listen():
                    if message['type'] == 'message':
                        data = json.loads(message['data'])
                        data = ValueMessage(**data)
                        success = self.settings.update(key=data.key, value=data.value)
                        if success:
                            logger.info(f"Received an update of global settings from other node for key `{data.key}`, value: {data.value}", extra=ExtraInfo.build('GlobalSettingsBroadcaster', self))
                break
            except JSONDecodeError as e:
                logger.error(f"Could not decode message from broadcaster. details: {str(e)}",
                             extra=ExtraInfo.build('GlobalSettingsBroadcaster', self, error_number="GSB0002"))
            except (TypeError, ValidationError):
                logger.error("Incorrect message from settings broadcaster", extra=ExtraInfo.build('GlobalSettingsBroadcaster', self, error_number="GSB0001"))
            except Exception:
                logger.info("Trying to reconnect to Redis...", extra=ExtraInfo.build('GlobalSettingsBroadcaster', self))
                sleep(5)


    def publish(self, key, value) -> bool:
        try:
            payload = ValueMessage(key=key, value=value)
            self.redis.publish(self.channel, payload.model_dump_json())
            logger.info(f"Global setting for key `{key}` have been broadcast to other nodes, payload: {payload}", extra=ExtraInfo.build('GlobalSettingsBroadcaster', self))
            return True
        except redis.exceptions.ConnectionError as e:
            logger.error(f"Connection lost to redis. Details: {str(e)}",
                        extra=ExtraInfo.build('GlobalSettingsBroadcaster', self, error_number="GSB0003"))

            return False

    def start_background_listener(self):
        thread = Thread(target=self._listen_for_messages)
        thread.daemon = True
        thread.start()


class GlobalSettings(metaclass=Singleton):

    def __init__(self):
        self.db = {}
        self.cs = ConfigurationService()

    async def _save_in_db(self, key, value):
        configuration = Configuration(
            id=key,
            name=f"System wide env variable {key}",
            timestamp=now_in_utc(),
            config=value,
            description=f"Default value for {key}",
            enabled=True,
            tags=['settings']
        )
        logger.info(f'Global setting for key `{key}` has changed. Data have been stored in the database.', extra=ExtraInfo.build('GlobalSettings', self))
        await self.cs.upsert(configuration)

    async def _broadcast_value(self, key, value) -> bool:
        broadcaster = GlobalSettingsBroadcaster()
        success =broadcaster.publish(key, value)

        # Wait a second and check the value
        await asyncio.sleep(1)
        new_value = await self.get(key)
        if new_value != value:
            logger.warning(f"Value may not have been broadcast or have changed within 1 sec.", extra=ExtraInfo.build('GlobalSettings', self))

        return success

    async def _save(self, key, value):

        # Save in storage
        await self._save_in_db(key, value)

        # Propagate
        if not await self._broadcast_value(key, value):
            raise ValueError(f"Could not save global setting value.")

    async def has(self, key) -> bool:
        result = await self.get(key)
        return result is not None

    def update(self, key, value) -> bool:

        # Update only updates the value in memory and does not save it in db or broadcast to other nodes.

        if key in self.db and self.db[key] == value:
            return False
        self.db[key] = value
        return True

    async def set(self, key, value) -> bool:
        if self.update(key, value):
            await self._save(key, value)
            return True

        return False

    async def get(self, key, default=None):
        if key in self.db:
            return self.db[key]

        logger.info(f"Global setting data {key} loaded from database", extra=ExtraInfo.build('GlobalSettings', self))
        record = await self.cs.load_by_id(key)
        if record.exists():
            # set value and return
            configuration = record.map_to_object(map_to_configuration)
            self.db[key] = configuration.config

            return self.db[key]

        # Use default value

        if default is None:
            return None

        # Save in storage
        await self._save(key, default)

        return default


if __name__ == "__main__":
    async def main():
        with ServerContext(Context(production=False)):
            x = GlobalSettings()

            broadcaster = GlobalSettingsBroadcaster()
            broadcaster.start_background_listener()
            while True:
                sleep(3)
                print(await x.get("risto"))
                sleep(1)
                await x.set("risto", random.random())


    asyncio.run(main())
