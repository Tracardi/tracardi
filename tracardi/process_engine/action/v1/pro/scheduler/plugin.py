from pydantic import BaseModel

from tracardi.domain.entity import Entity
from tracardi.domain.scheduler_config import SchedulerConfig
from tracardi.domain.resource import ResourceCredentials
from tracardi.service.storage.driver import storage
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi.service.plugin.domain.result import Result


class Configuration(BaseModel):
    source: Entity
    event_type: str
    properties: str = "{}"
    postpone: str


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
            license="MIT",
            author="Risto Kowaczewski",
            init= {
                "source": {
                  "id": ""
                },
                "event_type": "",
                "properties": "{}",
                "postpone": "+1m"
            }
        ),
        metadata=MetaData(
            name='Schedule event',
            desc='This plugin schedules events',
            icon='calendar',
            group=["Time"],
            tags=["Pro", "Scheduler"],
            pro=True,
        )
    )
