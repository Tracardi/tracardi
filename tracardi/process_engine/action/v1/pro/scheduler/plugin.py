import json
import logging
from datetime import datetime, timedelta

import tracardi.config
from tracardi.domain.scheduler_config import SchedulerConfig
from tracardi.exceptions.log_handler import log_handler
from tracardi.process_engine.action.v1.pro.scheduler.model.configuration import Configuration
from tracardi.process_engine.action.v1.pro.scheduler.service.schedule_client import SchedulerClient
from tracardi.service.notation.dict_traverser import DictTraverser
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result

logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)
logger.setLevel(tracardi.config.tracardi.logging_level)
logger.addHandler(log_handler)


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class SchedulerPlugin(ActionRunner):

    credentials: SchedulerConfig
    config: Configuration

    async def set_up(self, init):
        config = validate(init)
        resource = await storage.driver.resource.load(config.resource.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=SchedulerConfig)

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            client = SchedulerClient(tracardi.config.tracardi.tracardi_scheduler_host)
            schedule_at = datetime.utcnow() + timedelta(seconds=self.config.postpone)
            schedule_at = f'{str(schedule_at)}+00:00'

            properties = json.loads(self.config.properties)
            dot = self._get_dot_accessor(payload)
            reshaper = DictTraverser(dot)
            properties = reshaper.reshape(properties)

            if self.config.source.id == '@current-source':
                event_source_id = self.event.source.id
            else:
                event_source_id = self.config.source.id

            result = await client.schedule(
                schedule_at=schedule_at,
                callback_host=self.credentials.callback_host,
                source_id=event_source_id,
                profile_id=self.profile.id if self.profile is not None else None,
                session_id=self.session.id if self.session is not None else None,
                event_type=self.config.event_type,
                properties=properties,
                context=self.event.context,
                request=self.event.request
            )

            response = {
                "response": {
                    "id": result.id,
                    "time": result.time,
                    "key": result.key,
                    "origin": result.origin,
                    "server": tracardi.config.tracardi.tracardi_scheduler_host
                },
                "payload": payload
            }

            message = f"Scheduled task id: {result.id}"
            self.console.log(message)
            logger.info(message)

            return Result(port="response", value=response)
        except Exception as e:
            logger.error(str(e))
            self.console.error(str(e))
            return Result(port="error", value={
                "error": str(e),
                "payload": payload
            })


