from tracardi.process_engine.action.v1.connectors.matomo.client import MatomoClient, MatomoClientException
from tracardi.domain.resource import ResourceCredentials
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.storage.driver import storage
from .model.config import Config


def validate(config: dict) -> Config:
    return Config(**config)


class SendEventToMatomoAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'SendEventToMatomoAction':
        config = Config(**kwargs)
        credentials = (await storage.driver.resource.load(config.source.id)).credentials
        return SendEventToMatomoAction(config, credentials)

    def __init__(self, config: Config, credentials: ResourceCredentials):
        self.config = config
        self.client = MatomoClient(**credentials.get_credentials(self))

    async def run(self, payload):
        dot = self._get_dot_accessor(payload)

        data = {
            "action_name": self.event.type,
            "_id": self.profile.id.replace("-", ""),
            "apiv": 1,
            "_cvar": [{key: value} for key, value in self.event.properties.items()],
            "_idvc": self.profile.stats.visits,
            #"_idts": await storage.driver.session.get_first_session_date(self.profile.id)
            #"res": resolution,
            "h": self.event.metadata.time.insert.hour,
            "m": self.event.metadata.time.insert.minute,
            "s": self.event.metadata.time.insert.second,
            "cookie": 0,
            #"ua": user agent header,
            #"lang": accept language header,
            "uid": self.profile.id,
            "new_visit": 1,
        }

        if self.session is not None:
            data["cvar"] = self.session.context
            data["pv_id"] = self.session.id[0:6]

        if self.profile.metadata.time.lastVisit is not None:
            data["_viewts"] = self.profile.metadata.time.lastVisit.timestamp()

        if self.config.urlref is not None:
            data["urlref"] = dot[self.config.urlref]

        if self.config.rcn is not None:
            data["_rcn"] = dot[self.config.rcn]

        if self.config.rck is not None:
            data["_rck"] = dot[self.config.rck]

        if self.config.search is not None:
            data["search"] = dot[self.config.search]

        if self.config.search_cat is not None:
            data["search_cat"] = dot[self.config.search_cat]

        if self.config.id_goal is not None:
            data["idgoal"] = self.config.id_goal

        if self.config.revenue is not None:
            data["revenue"] = dot[self.config.revenue]

        if self.event.metadata.time.process_time is not None:
            data["gt_ms"] = int(self.event.metadata.time.process_time * 1000)

        if self.event.context.get("page", {"url": None}).get("url") is not None:
            data["url"] = self.event.context["page"]["url"]

        try:
            await self.client.send_event(1, data)
            return Result(port="response", value=payload)

        except MatomoClientException as e:
            return Result(port="error", value=str(e))


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='SendEventToMatomoAction',
            inputs=["payload"],
            outputs=["response", "error"],
            version='0.6.2',
            license="MIT",
            author="Dawid Kruk",
            #manual,
            init={
                "source": {
                    "id": None,
                    "name": None
                }
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="Matomo resource",
                                description="Please select your Matomo resource, containing Matomo URL and token.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "matomo"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Send event to Matomo',
            desc='Sends currently processed event to Matomo.',
            icon='plugin',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "response": PortDoc(desc="This port returns payload if everything is OK."),
                    "error": PortDoc(desc="This port gets triggered if an error occurs.")
                }
            )
        )
    )
