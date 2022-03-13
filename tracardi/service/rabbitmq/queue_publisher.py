import logging
from kombu import Exchange, Queue, Producer
from tracardi.config import tracardi
from .queue_config import QueueConfig

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(tracardi.logging_level)


class QueuePublisher:

    def __init__(self, conn, queue_config: QueueConfig):
        self.conn = conn
        channel = conn.channel()
        exchange = Exchange(queue_config.name, queue_config.queue_type, durable=queue_config.durable)
        queue = Queue(queue_config.name, exchange=exchange, routing_key=queue_config.routing_key)
        queue.maybe_bind(self.conn)
        queue.declare()

        self.producer = Producer(exchange=exchange,
                                 channel=channel,
                                 routing_key=queue.routing_key,
                                 serializer=queue_config.serializer,
                                 compression=queue_config.compression,
                                 auto_declare=queue_config.auto_declare)

    def publish(self, payload):
        return self.producer.publish(payload)  # , compression='bzip2'
