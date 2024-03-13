from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, Form, FormGroup, \
    FormField, FormComponent
from tracardi.service.plugin.runner import ActionRunner
from .model.config import Config, MixPanelCredentials
from tracardi.service.domain import resource as resource_db
from tracardi.process_engine.action.v1.connectors.mixpanel.client import MixPanelAPIClient
from tracardi.service.plugin.domain.result import Result
from datetime import datetime
from tracardi.service.notation.dict_traverser import DictTraverser


def validate(config: dict) -> Config:
    return Config(**config)


class MixPanelSender(ActionRunner):

    client: MixPanelAPIClient
    config: Config

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.config = config
        self.client = MixPanelAPIClient(
            **resource.credentials.get_credentials(self, MixPanelCredentials).model_dump()
        )
        self.client.set_retries(self.node.on_connection_error_repeat)

    async def run(self, payload: dict, in_edge=None) -> Result:
        dot = self._get_dot_accessor(payload)
        traverser = DictTraverser(dot)

        event_type = dot["event@type"]
        profile_id = dot["event@profile.id"] if "event@profile.id" in dot else ""
        event_id = dot["event@id"]
        time = dot["event@metadata.time.insert"].timestamp() if isinstance(dot["event@metadata.time.insert"], datetime)\
            else dot["event@metadata.time.insert"]

        try:
            result = await self.client.send(
                event_type=event_type,
                event_id=event_id,
                profile_id=profile_id,
                time=int(time),
                **traverser.reshape(self.config.mapping)
            )
            if result["status"] != 1:
                self.console.error(result["error"])
                return Result(port="error", value=payload)
            return Result(port="success", value=payload)

        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='MixPanelSender',
            inputs=["payload"],
            outputs=["success", "error"],
            version='0.6.1',
            license="MIT + CC",
            author="Dawid Kruk",
            manual="send_to_mixpanel_action",
            init={
                "source": {
                    "name": None,
                    "id": None
                },
                "mapping": {}
            },
            form=Form(
                groups=[
                    FormGroup(
                        name="Plugin configuration",
                        fields=[
                            FormField(
                                id="source",
                                name="MixPanel resource",
                                description="Please select your MixPanel resource containing your token and server "
                                            "prefix.",
                                component=FormComponent(type="resource", props={"label": "Resource", "tag": "mixpanel"})
                            ),
                            FormField(
                                id="mapping",
                                name="Additional fields mapping",
                                description="You can add additional fields mapping in form of key-value pairs. Feel "
                                            "free to use dot paths.",
                                component=FormComponent(type="keyValueList", props={"label": "Mapping"})
                            )
                        ]
                    )
                ]
            )
        ),
        metadata=MetaData(
            name='Register event',
            brand='MixPanel',
            desc='Sends processed event to MixPanel project.',
            icon='mixpanel',
            group=["Mixpanel"],
            tags=['analytics'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "success": PortDoc(desc="This port returns given payload when the action was successful."),
                    "error": PortDoc(desc="This port returns given payload when an error occurs.")
                }
            )
        )
    )
