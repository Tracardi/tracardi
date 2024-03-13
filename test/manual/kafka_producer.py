import json
from time import sleep

from aiokafka import AIOKafkaProducer
import asyncio
from aiokafka.helpers import create_ssl_context

async def send_one():
    ssl_context = create_ssl_context()  # todo from config
    producer = AIOKafkaProducer(
        bootstrap_servers='localhost:9092',  # todo from config
        # ssl_context=ssl_context,
        # security_protocol='SASL_SSL',  # todo from config
        # sasl_mechanism='PLAIN',  # todo from config
        # sasl_plain_username='testgua',  # todo from config
        # sasl_plain_password='c4321687-654b-40e7-ae9f-749e47e6f6a5',  # todo from config
    )  # todo from config

    # producer = AIOKafkaProducer(
    #     bootstrap_servers='localhost:9092')
    # Get cluster layout and initial topic/partition leadership information
    await producer.start()
    try:
        # Produce message
        message = {"text": "message"}
        json_text = json.dumps(message)
        print(await producer.send_and_wait('test-trc', value=json_text.encode()))
        # sleep(100)
    finally:
        # Wait for all pending messages to be delivered or expire.
        await producer.stop()


asyncio.run(send_one())
