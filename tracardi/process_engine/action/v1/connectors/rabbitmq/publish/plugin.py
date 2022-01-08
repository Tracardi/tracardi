from kombu import Connection
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.action_runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.storage.driver import storage

from tracardi.domain.resource import ResourceCredentials
from .model.configuration import PluginConfiguration
from .model.rabbit_configuration import RabbitSourceConfiguration
from .service.queue_publisher import QueuePublisher


def validate(config: dict) -> PluginConfiguration:
    return PluginConfiguration(**config)


class RabbitPublisherAction(ActionRunner):

    @staticmethod
    async def build(**kwargs) -> 'RabbitPublisherAction':
        config = validate(kwargs)
        resource = await storage.driver.resource.load(config.source.id)
        return RabbitPublisherAction(config, resource.credentials)

    def __init__(self, config: PluginConfiguration, credentials: ResourceCredentials):
        self.source = credentials.get_credentials(self, output=RabbitSourceConfiguration)
        self.config = config
        if self.config.queue.compression == "none":
            self.config.queue.compression = None

    async def run(self, payload):
        try:
            with Connection(self.source.uri, connect_timeout=self.source.timeout) as conn:
                queue_publisher = QueuePublisher(conn, config=self.config)
                queue_publisher.publish(payload)
        except Exception as e:
            self.console.error(str(e))
            return Result(port="error", value={"error": str(e), "payload": payload})

        return Result(port="payload", value=payload)


def register() -> Plugin:
    return Plugin(
        start=False,
        spec=Spec(
            module=__name__,
            className='RabbitPublisherAction',
            inputs=["payload"],
            outputs=["payload", "error"],
            version='0.6.1',
            license="MIT",
            author="Risto Kowaczewski",
            manual="rabbit_publisher_action",
            init={
                "source": {
                    "id": None
                },
                "queue": {
                    "name": None,
                    "routing_key": None,
                    "queue_type": "direct",
                    "compression": None,
                    "auto_declare": True,
                    "serializer": "json"
                }
            },
            form=Form(groups=[
                FormGroup(
                    name="RabbitMQ connection settings",
                    fields=[
                        FormField(
                            id="source",
                            name="RabbitMQ resource",
                            description="Select RabbitMQ resource. Authentication credentials will be used to "
                                        "connect to RabbitMQ server.",
                            component=FormComponent(
                                type="resource",
                                props={"label": "resource", "tag": "rabbitmq"})
                        )
                    ]
                ),
                FormGroup(
                    name="RabbitMQ queue settings",
                    fields=[
                        FormField(
                            id="queue.name",
                            name="Queue name",
                            description="Type queue name where the payload will be sent.",
                            component=FormComponent(type="text", props={"label": "Queue name"})
                        ),
                        FormField(
                            id="queue.routing_key",
                            name="Routing key",
                            description="Type routing key name.",
                            component=FormComponent(type="text", props={"label": "Routing key"})
                        ),
                        FormField(
                            id="queue.auto_declare",
                            name="Auto create queue",
                            description="Create queue on first published message.",
                            component=FormComponent(type="bool", props={
                                "label": "Should RabbitMQ create queue if it does not exist."
                            })
                        ),
                        FormField(
                            id="queue.queue_type",
                            name="Queue type",
                            description="Select queue type.",
                            component=FormComponent(type="select", props={
                                "label": "Queue type",
                                "items": {
                                    "direct": "Direct",
                                    "fanout": "Fanout",
                                    "topic": "Topic",
                                    "headers": "Headers"
                                }
                            })
                        ),

                    ]),
                    FormGroup(
                        name="RabbitMQ advanced queue settings",
                        fields=[
                            FormField(
                                id="queue.serializer",
                                name="Serialization type",
                                description="Select serialization type.",
                                component=FormComponent(type="select", props={
                                    "label": "Serialization type",
                                    "items": {
                                        "json": "JSON",
                                        "xml": "XML",
                                    }
                                })
                            ),
                            FormField(
                                id="queue.compression",
                                name="Data compression",
                                description="Select if the data should be compressed and with what algorithm.",
                                component=FormComponent(type="select", props={
                                    "label": "Compression",
                                    "style": {"width": "200px"},
                                    "items": {
                                        "none": "No compression",
                                        "bzip2": "Compress with bzip2",
                                        "gzip": "Compress with gzip",
                                    }
                                })
                            )
                        ]
                    )
            ]),

        ),
        metadata=MetaData(
            name='Rabbitmq publish',
            desc='Publishes payload to rabbitmq.',
            icon='rabbitmq',
            group=["Connectors"],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns input payload on success."),
                    "error": PortDoc(desc="Returns input payload and error on failure."),
                }
            )
        )
    )
