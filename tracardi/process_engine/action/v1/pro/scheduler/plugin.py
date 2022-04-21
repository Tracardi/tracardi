import json
from datetime import datetime, timedelta

import tracardi.config
from tracardi.domain.scheduler_config import SchedulerConfig
from tracardi.domain.resource import ResourceCredentials
from tracardi.process_engine.action.v1.pro.scheduler.model.configuration import Configuration
from tracardi.process_engine.action.v1.pro.scheduler.service.schedule_client import SchedulerClient
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.domain.result import Result


def validate(config: dict) -> Configuration:
    return Configuration(**config)


class SchedulerPlugin(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'SchedulerPlugin':
        config = validate(kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        plugin = SchedulerPlugin(config, resource.credentials)
        return plugin

    def __init__(self, config: Configuration, credentials: ResourceCredentials):
        self.config = config
        self.credentials = credentials.get_credentials(
            self,
            output=SchedulerConfig)  # type: SchedulerConfig

    async def run(self, payload):

        run_in_background = True

        client = SchedulerClient(tracardi.config.tracardi.tracardi_pro_host)
        schedule_at = str(datetime.utcnow() + timedelta(seconds=self.config.postpone))
        result = await client.schedule(
            schedule_at=schedule_at,
            callback_host=self.credentials.callback_host,
            source_id=self.event.source.id,
            profile_id=self.profile.id,
            session_id=self.session.id,
            event_type=self.config.event_type,
            properties=json.loads(self.config.properties),
            context=self.event.context
        )
        print(f"XXX {result.id}")
        if not run_in_background:
            return Result(port="response", value=None)
        else:
            return Result(port="response", value=None)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.pro.scheduler.plugin',
            className='SchedulerPlugin',
            inputs=["payload"],
            outputs=['response', 'error'],
            version='0.6.2',
            license="Tracardi Pro License",
            author="Risto Kowaczewski",
            init={
                "source": {
                    "id": ""
                },
                "event_type": "",
                "properties": "{}",
                "postpone": 1
            },
            form=Form(groups=[
                FormGroup(
                    name="Scheduled event settings",
                    description="This action will schedule event with defined event type and properties. "
                                "Event will have the same profile as current event.",
                    fields=[
                        FormField(
                            id="source",
                            name="Scheduler service",
                            description="Please select your scheduler service.",
                            component=FormComponent(type="resource", props={"label": "Service", "tag": "schedule"})
                        ),
                        FormField(
                            id="postpone",
                            name="Event delay in seconds",
                            component=FormComponent(type="text", props={
                                "label": "delay in seconds"
                            })
                        ),
                    ]
                ),
                FormGroup(
                    name="Event settings",
                    fields=[
                        FormField(
                            id="event_type",
                            name="Event type",
                            description="Type event type",
                            component=FormComponent(type="text", props={"label": "Event type"})
                        ),
                        FormField(
                            id="properties",
                            name="Properties",
                            description="Type event properties.",
                            component=FormComponent(type="json", props={"label": "Event properties"})
                        )
                    ]
                )
            ]
            )
        ),
        metadata=MetaData(
            name='Schedule event',
            desc='This plugin schedules events',
            icon='calendar',
            group=["Time"],
            tags=["pro", "scheduler", "postpone"],
            pro=False,
        )
    )
