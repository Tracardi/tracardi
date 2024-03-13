from aiokafka import AIOKafkaConsumer
import asyncio

from aiokafka.helpers import create_ssl_context


async def consume():
    ssl_context = create_ssl_context()  # todo from config
    consumer = AIOKafkaConsumer(
        'topic1',  # todo from config
        bootstrap_servers='localhost:9092',  # todo from config
        # ssl_context=ssl_context,
        # security_protocol='SASL_SSL',  # todo from config
        # sasl_mechanism='PLAIN',  # todo from config
        # sasl_plain_username='5jOXuSSYst1nOaucr9H1WL',  # todo from config
        # sasl_plain_password='be2725d5-4f21-47e2-a87d-de15cdf564a0',  # todo from config
        group_id=None,
        consumer_timeout_ms=10000,
        session_timeout_ms=45000
    )  # todo from config

    await consumer.start()
    try:
        i = 0
        print("start")
        async for msg in consumer:
            i += 1
            print(i)
            print("consumed: ", msg.topic, msg.partition, msg.offset,
                  msg.key, msg.value, msg.timestamp, msg.headers)
    finally:
        # Will leave consumer group; perform autocommit if enabled.
        await consumer.stop()


asyncio.run(consume())
