import json
import logging
from datetime import datetime, timedelta

import tracardi.config
from tracardi.domain.scheduler_config import SchedulerConfig
from tracardi.domain.resource import ResourceCredentials
from tracardi.exceptions.log_handler import log_handler
from tracardi.process_engine.action.v1.pro.scheduler.model.configuration import Configuration
from tracardi.process_engine.action.v1.pro.scheduler.service.schedule_client import SchedulerClient
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
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
        resource = await storage.driver.resource.load(config.source.id)

        self.config = config
        self.credentials = resource.credentials.get_credentials(self, output=SchedulerConfig)

    async def run(self, payload: dict, in_edge=None) -> Result:
        try:
            client = SchedulerClient(tracardi.config.tracardi.tracardi_scheduler_host)
            schedule_at = str(datetime.utcnow() + timedelta(seconds=self.config.postpone))
            result = await client.schedule(
                schedule_at=schedule_at,
                callback_host=self.credentials.callback_host,
                source_id=self.event.source.id,
                profile_id=self.profile.id if self.profile is not None else None,
                session_id=self.session.id if self.session is not None else None,
                event_type=self.config.event_type,
                properties=json.loads(self.config.properties),
                context=self.event.context
            )

            response = {
                "response": {
                    "id": result.id,
                    "time": result.time,
                    "key": result.key,
                    "origin": result.origin,
                    "server": tracardi.config.tracardi.tracardi_pro_host
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


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.pro.scheduler.plugin',
            className='SchedulerPlugin',
            inputs=["payload"],
            outputs=['response', 'error'],
            version='0.7.1',
            license="Tracardi Pro License",
            author="Risto Kowaczewski"
        ),
        metadata=MetaData(
            name='Schedule event',
            desc='This plugin schedules events',
            icon='calendar',
            group=["Time"],
            tags=["pro", "scheduler", "postpone", "delay", "event"],
            pro=True,
        )
    )
