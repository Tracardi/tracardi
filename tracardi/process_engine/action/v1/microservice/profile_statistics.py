import json
from datetime import datetime
from aiohttp import ClientResponse
from pydantic import BaseModel, AnyHttpUrl

from tracardi.service.storage.driver import storage
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent
from tracardi_plugin_sdk.domain.result import Result
from tracardi.domain.credentials import Credentials
from tracardi.domain.stat_payload import StatPayload
from tracardi.service.microservice import MicroserviceApi
from tracardi.domain.entity import Entity


class ResourceConfiguration(BaseModel):
    url: AnyHttpUrl = "http://localhost:12345"
    username: str = "admin"
    password: str = "admin"


class Configuration(BaseModel):
    source: Entity
    timeout: int = 15


def validate(config: dict):
    return Configuration(**config)


class ProfileStatisticsApi(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'ProfileStatisticsApi':
        config = validate(kwargs)
        source = await storage.driver.resource.load(config.source.id)
        plugin = ProfileStatisticsApi(config, ResourceConfiguration(**source.config))
        return plugin

    def __init__(self, config: Configuration, source: ResourceConfiguration):
        self.source = source
        self.config = config
        self.client = MicroserviceApi(
            self.source.url,
            credentials=Credentials(
                username=self.source.username,
                password=self.source.password
            )
        )

    async def run(self, payload):

        # todo run in background
        print(self.node)
        self.node.outputs = []
        response = await self._call_endpoint()

        result = {
            "status": response.status,
            "json": await response.json()
        }

        if 200 <= response.status < 400:
            return Result(port="response", value=result), Result(port="error", value=None)
        else:
            return Result(port="response", value=None), Result(port="error", value=result)

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
            module='tracardi.process_engine.action.v1.microservice.profile_statistics',
            className='ProfileStatisticsApi',
            inputs=["payload"],
            outputs=['response', 'error'],
            version='0.6.0',
            license="MIT",
            author="Risto Kowaczewski",
            init={
                "source": {
                    "id": ""
                },
                "timeout": 5
            },
            form=Form(groups=[
                FormGroup(
                    fields=[
                        FormField(
                            id="source",
                            name="Tracardi PRO - Stats service",
                            description="Select Tracardi PRO - Stats service resource.",
                            required=True,
                            component=FormComponent(type="resource", props={"label": "resource"})
                        )
                    ]
                ),
                FormGroup(
                    fields=[
                        FormField(
                            id="timeout",
                            name="Service time-out",
                            component=FormComponent(type="text", props={"time-out": "15"})
                        )
                    ]
                ),
            ]),
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


if __name__ == "__main__":
    from tracardi.domain.context import Context
    from tracardi.domain.entity import Entity
    from tracardi.domain.event import Event, Tags
    from tracardi.domain.value_object.operation import Operation
    from tracardi.domain.session import Session
    from tracardi_plugin_sdk.service.plugin_runner import run_plugin

    init = {
        "source": {
            "id": "d74cad8c-0b17-4d1c-8d08-20c0df038284",
            "timeout": 15
        }
    }

    payload = {
        "a": 1
    }

    tags = Tags(values=("tag1", "tag2"))
    session = Session(id="1", operation=Operation(new=True))

    result = run_plugin(
        ProfileStatisticsApi,
        init,
        payload,
        profile=Entity(id="profile-id"),
        session=session,
        event=Event(id="2", type="page-view", tags=tags, source=Entity(id="3"), session=session, context=Context())
    )

    print(result)

    result = run_plugin(
        ProfileStatisticsApi,
        init,
        payload,
        profile=Entity(id="profile-id"),
        session=session,
        event=Event(id="2", type="page-view", tags=tags, source=Entity(id="3"), session=session, context=Context())
    )

    # print(result)
