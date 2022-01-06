import logging
from kombu import Exchange, Queue, Producer
from ..model.configuration import PluginConfiguration

logging.basicConfig(format='%(asctime)s %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class QueuePublisher:

    def __init__(self, conn, config: PluginConfiguration):
        self.conn = conn
        self.queue_config = config
        channel = conn.channel()
        exchange = Exchange(config.queue.name, config.queue.queue_type, durable=config.queue.durable)
        queue = Queue(config.queue.name, exchange=exchange, routing_key=config.queue.routing_key)
        queue.maybe_bind(self.conn)
        queue.declare()

        self.producer = Producer(exchange=exchange,
                                 channel=channel,
                                 routing_key=queue.routing_key,
                                 serializer=config.queue.serializer,
                                 compression=config.queue.compression,
                                 auto_declare=config.queue.auto_declare)

    def publish(self, payload):
        return self.producer.publish(payload)  # , compression='bzip2'
