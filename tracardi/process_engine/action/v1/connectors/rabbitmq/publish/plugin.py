from kombu import Connection
from tracardi.service.plugin.domain.register import Plugin, Spec, MetaData, Form, FormGroup, FormField, FormComponent, \
    Documentation, PortDoc
from tracardi.service.plugin.runner import ActionRunner
from tracardi.service.plugin.domain.result import Result
from tracardi.service.domain import resource as resource_db
from .model.configuration import PluginConfiguration
from .model.rabbit_configuration import RabbitSourceConfiguration
from .service.queue_publisher import QueuePublisher


def validate(config: dict) -> PluginConfiguration:
    return PluginConfiguration(**config)


class RabbitPublisherAction(ActionRunner):

    config: PluginConfiguration
    source: RabbitSourceConfiguration

    async def set_up(self, init):
        config = validate(init)
        resource = await resource_db.load(config.source.id)

        self.source = resource.credentials.get_credentials(self, output=RabbitSourceConfiguration)
        self.config = config

    async def run(self, payload: dict, in_edge=None) -> Result:
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
            license="MIT + CC",
            author="Risto Kowaczewski",
            manual="rabbit_publisher_action",
            init={
                "source": {
                    "id": "",
                    "name": ""
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
                                props={"label": "resource", "tag": "rabbitmq", "pro": True})
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
            tags=['queue'],
            documentation=Documentation(
                inputs={
                    "payload": PortDoc(desc="This port takes payload object.")
                },
                outputs={
                    "payload": PortDoc(desc="Returns input payload on success."),
                    "error": PortDoc(desc="Returns input payload and error on failure."),
                }
            ),
            pro=True
        )
    )
