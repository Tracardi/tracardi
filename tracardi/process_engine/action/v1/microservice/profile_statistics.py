import json
from datetime import datetime

import aiohttp
from pydantic import BaseModel, AnyHttpUrl
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.domain.result import Result

from tracardi.domain.stat_payload import StatPayload


class Configuration(BaseModel):
    url: AnyHttpUrl = "http://localhost:12345"
    timeout: int = 15


def validate(config: dict):
    return Configuration(**config)


class ProfileStatisticsApi(ActionRunner):

    def __init__(self, **kwargs):
        self.config = validate(kwargs)

    async def run(self, payload):

        # todo run in background

        # todo Authorize

        timeout = aiohttp.ClientTimeout(total=self.config.timeout)
        async with aiohttp.ClientSession(timeout=timeout) as session:

            stats = StatPayload(
                date=datetime.utcnow(),
                new_session=self.session.operation.new,
                event_type=self.event.type,
                event_tags=list(self.event.tags.values)
            )

            # Converts datetime
            payload = json.loads(json.dumps(stats.dict(), default=str))

            async with session.request(
                    method="POST",
                    url="{}/stat/{}".format(str(self.config.url), self.profile.id),
                    json=payload
            ) as response:

                # todo better response

                result = {
                    "status": response.status,
                    "json": await response.json()
                }

                if response.status in [200, 201, 202, 203, 204]:
                    return Result(port="response", value=result), Result(port="error", value=None)
                else:
                    return Result(port="response", value=None), Result(port="error", value=result)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module='tracardi.process_engine.action.v1.microservice.profile_statistics',
            className='ProfileStatisticsApi',
            inputs=["payload"],
            outputs=['payload'],
            version='0.1',
            license="MIT",
            author="Risto Kowaczewski",
            init={}
        ),
        metadata=MetaData(
            name='Profile statistics',
            desc='This plugin connects to profile statistics microservice',
            type='flowNode',
            width=250,
            height=100,
            icon='pie-chart',
            group=["Stats", "Professional"],
            tags=["Pro", "Statistics"],
            pro=True
        )
    )
