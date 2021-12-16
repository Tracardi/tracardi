import json
from datetime import datetime

import asyncio
from aiohttp import ClientResponse
from pydantic import BaseModel, AnyHttpUrl

from tracardi.domain.event_source import EventSource
from tracardi.domain.resource import ResourceCredentials
from tracardi.service.storage.driver import storage
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from tracardi.domain.credentials import Credentials
from tracardi.domain.stat_payload import StatPayload
from tracardi.service.microservice import MicroserviceApi
from tracardi.domain.entity import Entity


class ServiceConfiguration(BaseModel):
    callback_url: AnyHttpUrl


class Configuration(BaseModel):
    service: Entity
    timeout: int = 15


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class SchedulerPlugin(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'SchedulerPlugin':
        config = validate(kwargs)
        service = await storage.driver.raw.load(config.service.id, 'event-source', EventSource)
        plugin = SchedulerPlugin(config, service)
        return plugin

    def __init__(self, config: Configuration, service: EventSource):
        self.config = config
        # url must be build from token (schedule/event/token)
        self.client = MicroserviceApi(
            service.url,
            credentials=Credentials(
                username=service.username,
                password=service.password
            )
        )

    async def run(self, payload):

        # todo run in background

        run_in_background = True

        if not run_in_background:
            response = await self._call_endpoint()

            result = {
                "status": response.status,
                "json": await response.json()
            }

            if 200 <= response.status < 400:
                return Result(port="response", value=result), Result(port="error", value=None), Result(port="payload", value=payload)
            else:
                return Result(port="response", value=None), Result(port="error", value=result), Result(port="payload", value=payload)

        else:
            asyncio.create_task(self._call_endpoint())
            return Result(port="response", value=None), Result(port="payload", value=payload), Result(port="error", value=None)

    async def _call_endpoint(self) -> ClientResponse:

        stats = StatPayload(
            date=datetime.utcnow(),
            new_session=self.session.operation.new,
            event_type=self.event.type,
            event_tags=list(self.event.tags.values)
        )

        payload = json.loads(json.dumps(stats.dict(), default=str))

        return await self.client.call(
            endpoint="/stat/{}".format(self.profile.id),
            method="POST",
            data=payload
        )


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.pro.scheduler.plugin',
            className='SchedulerPlugin',
            inputs=["payload"],
            outputs=['response', 'error', 'payload'],
            version='0.6.0',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "service": {
                    "id": ""
                },
                "timeout": 15
            },
            #
            # Formularz pobierany z /schedule/config/form/
            form=Form(groups=[
                FormGroup(
                    name="Service source",
                    fields=[
                        FormField(
                            id="service",
                            name="Tracardi PRO - service",
                            component=FormComponent(type="resource", props={"label": "resource", "tag": "scheduler"})
                        ),
                        FormField(
                            id="timeout",
                            name="Callback timeout",
                            component=FormComponent(type="text", props={"label": "Time-out"})
                        )
                    ]
                )
            ]),
        ),
        metadata=MetaData(
            name='Scheduler',
            desc='This plugin schedules events',
            icon='calendar',
            group=["Time"],
            tags=["Pro", "Scheduler"],
            pro=True,
        )
    )

