import json
from _pulsar import InitialPosition

from pulsar import Client, ConsumerType

from com_tracardi.service.tracking.queue.pulsar_topics import pulsar_topics
from tracardi.domain.entity import Entity

# Pulsar service URL
service_url = 'pulsar://localhost:6650'

# Create a Pulsar client instance
client = Client(service_url)

# Create a consumer instance
consumer = client.subscribe(pulsar_topics.event_topic,
                            'my-subscription',
                            consumer_type=ConsumerType.Shared,
                            initial_position=InitialPosition.Earliest
                            )

try:
    while True:
        # Receive a message
        msg = consumer.receive()
        try:
            d = msg.data().decode('utf-8')
            d = json.loads(d)
            # if isinstance(d['_data'], list):
            #     d = d['_data'][0]
            # else:
            #     d= d['_data']
            # Do something with the message
            print(d)

            # Acknowledge successful processing of the message
            consumer.acknowledge(msg)
        except Exception as e:
            print(f"Failed to process message: {e}")

            # Negative acknowledgement in case of processing failure
            consumer.negative_acknowledge(msg)
finally:
    # Close the consumer and client
    consumer.close()
    client.close()
