from tracardi.domain.resources.mqtt_resource import MqttResourceCredentials
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Documentation, PortDoc, FormGroup, Form, \
    FormField, FormComponent
from tracardi.service.plugin.domain.result import Result
from tracardi.service.plugin.runner import ActionRunner
import aiomqtt

from .model.config import Configuration
from tracardi.service.domain import resource as resource_db


def validate(config: dict):
    return Configuration(**config)


class MqttPublishAction(ActionRunner):
    credentials: MqttResourceCredentials
    config: Configuration

    async def set_up(self, init):
        configuration = validate(init)
        resource = await resource_db.load(configuration.source.id)

        self.config = configuration
        self.credentials = resource.credentials.get_credentials(self, output=MqttResourceCredentials)

    async def run(self, payload: dict, in_edge=None):
        try:
            async with aiomqtt.Client(self.credentials.url,
                                      port=self.credentials.port,
                                      username=self.credentials.username,
                                      password=self.credentials.password) as client:

                await client.publish(
                    self.config.topic,
                    payload=self.config.payload.encode(),
                    qos=int(self.config.qos),
                    retain=self.config.retain
                )

            return Result(port="payload", value=payload)
        except Exception as e:
            return Result(port="error", value={
                "message": str(e)
            })


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='MqttPublishAction',
            inputs=["payload"],
            outputs=["payload", "error"],
            version='0.8.1',
            license="MIT + CC",
            author="Risto Kowaczewski",
            init={
                "source": {
                    "id": "",
                    "name": ""
                },
                "topic": "",
                "payload": "{}",
                "qos": "0",
                "retain": False
            },
            form=Form(groups=[
                FormGroup(
                    name="MQTT Resource",
                    fields=[
                        FormField(
                            id="source",
                            name="MQTT resource",
                            description="Select MQTT resource. Credentials from selected resource will be used "
                                        "to connect to queue.",
                            component=FormComponent(type="resource", props={"label": "resource", "tag": "mqtt"})
                        )
                    ]
                ),
                FormGroup(
                    name="MQTT Payload and Topic",
                    fields=[
                        FormField(
                            id="topic",
                            name="Topic",
                            component=FormComponent(type="text", props={"label": "topic"})
                        ),
                        FormField(
                            id="payload",
                            name="Payload",
                            component=FormComponent(type="textarea", props={"label": "payload"})
                        ),
                        FormField(
                            id="qos",
                            name="Quality of service",
                            component=FormComponent(type="select", props={"label": "QoS", "items": {
                                "0": "0 - Fire and forget",
                                "1": "1 - At least once",
                                "2": "2 - Once and once only"
                            }})
                        ),
                        FormField(
                            id="retain",
                            name="Retain the message on the broker.",
                            component=FormComponent(type="bool", props={"label": "Retain"})
                        )
                    ]
                )
            ]
            )
        ),
        metadata=MetaData(
            name='MQTT publish',
            desc='Publishes payload to MQTT queue.',
            icon='mqtt',
            group=["MQTT"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="This port returns input payload."),
                    "error": PortDoc(desc="This port returns error object.")
                }
            )
        )
    )
